import json
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.firewall.manager import FirewallManager
from app.services.audit_service import AuditService
from app.services.redis_client import redis
from app.services.user_session_log_service import UserSessionLogService


class SessionService:
    firewall = FirewallManager()

    @staticmethod
    def _session_key(session_id: str) -> str:
        return f'session:{session_id}'

    @classmethod
    async def create_session(cls, username: str, ip: str, ports: list[int], db: AsyncSession | None = None) -> tuple[str, datetime]:
        session_id = str(uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
        payload = {'session_id': session_id, 'username': username, 'ip': ip, 'ports': ports, 'expires_at': expires_at.isoformat()}

        key = cls._session_key(session_id)
        ttl = settings.access_token_expire_minutes * 60
        await redis.set(key, json.dumps(payload), ex=ttl)
        await redis.zadd('session:expires', {session_id: expires_at.timestamp()})

        for port in ports:
            await cls.firewall.allow_ip_port(ip, port)

        await AuditService.log('session_created', payload)
        if db:
            await UserSessionLogService.log(db, session_id=session_id, username=username, ip=ip, action='online', actor=username)
        return session_id, expires_at

    @classmethod
    async def terminate_session(cls, session_id: str, actor: str = 'system', db: AsyncSession | None = None) -> None:
        key = cls._session_key(session_id)
        raw = await redis.get(key)
        if not raw:
            await redis.zrem('session:expires', session_id)
            return

        data = json.loads(raw)
        for port in data['ports']:
            await cls.firewall.revoke_ip_port(data['ip'], port)

        await redis.delete(key)
        await redis.zrem('session:expires', session_id)
        await AuditService.log('session_terminated', {'session_id': session_id, 'actor': actor})
        if db:
            await UserSessionLogService.log(
                db,
                session_id=session_id,
                username=data['username'],
                ip=data['ip'],
                action='offline',
                actor=actor,
            )

    @classmethod
    async def list_sessions(cls) -> list[dict]:
        result = []
        async for key in redis.scan_iter('session:*'):
            if key == 'session:expires':
                continue
            raw = await redis.get(key)
            if raw:
                result.append(json.loads(raw))
        return result

    @classmethod
    async def cleanup_expired(cls) -> int:
        now = datetime.now(timezone.utc).timestamp()
        expired = await redis.zrangebyscore('session:expires', 0, now)
        for sid in expired:
            await cls.terminate_session(sid)
        return len(expired)
