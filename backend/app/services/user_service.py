import json

from app.core.security import get_password_hash
from app.services.redis_client import redis


class UserService:
    @staticmethod
    async def init_admin() -> None:
        if await redis.exists('user:admin'):
            return
        await redis.set(
            'user:admin',
            json.dumps({'username': 'admin', 'password_hash': get_password_hash('admin123!'), 'is_active': True, 'is_admin': True}),
        )

    @staticmethod
    async def get_user(username: str) -> dict | None:
        data = await redis.get(f'user:{username}')
        return json.loads(data) if data else None

    @staticmethod
    async def list_users() -> list[dict]:
        users = []
        async for key in redis.scan_iter('user:*'):
            data = await redis.get(key)
            if data:
                users.append(json.loads(data))
        return users

    @staticmethod
    async def upsert_user(username: str, password: str, is_admin: bool = False) -> None:
        payload = {
            'username': username,
            'password_hash': get_password_hash(password),
            'is_active': True,
            'is_admin': is_admin,
        }
        await redis.set(f'user:{username}', json.dumps(payload))
