from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import UserSessionLogDB


class UserSessionLogService:
    @staticmethod
    async def log(session: AsyncSession, session_id: str, username: str, ip: str, action: str, actor: str = 'system') -> None:
        row = UserSessionLogDB(
            session_id=session_id,
            username=username,
            ip=ip,
            action=action,
            actor=actor,
            event_at=datetime.now(timezone.utc),
        )
        session.add(row)
        await session.commit()

    @staticmethod
    async def list_logs(session: AsyncSession, username: str | None = None, limit: int = 100) -> list[dict]:
        stmt = select(UserSessionLogDB)
        if username:
            stmt = stmt.where(UserSessionLogDB.username == username)
        stmt = stmt.order_by(UserSessionLogDB.event_at.desc()).limit(limit)
        result = await session.execute(stmt)
        rows = result.scalars().all()
        return [
            {
                'session_id': row.session_id,
                'username': row.username,
                'ip': row.ip,
                'action': row.action,
                'actor': row.actor,
                'event_at': row.event_at,
            }
            for row in rows
        ]
