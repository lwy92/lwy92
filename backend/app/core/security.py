from datetime import timedelta
import secrets

from passlib.context import CryptContext

from app.core.config import settings
from app.services.redis_client import redis

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


class AccessTokenService:
    @staticmethod
    def _token_key(token: str) -> str:
        return f'auth:token:{token}'

    @classmethod
    async def create_access_token(cls, subject: str, expires_delta: timedelta | None = None) -> str:
        """创建随机令牌并写入 Redis，不依赖 JWT。"""
        token = secrets.token_urlsafe(32)
        ttl_seconds = int((expires_delta or timedelta(minutes=settings.access_token_expire_minutes)).total_seconds())
        await redis.set(cls._token_key(token), subject, ex=ttl_seconds)
        return token

    @classmethod
    async def get_subject(cls, token: str) -> str | None:
        """根据令牌获取用户名。"""
        return await redis.get(cls._token_key(token))

    @classmethod
    async def revoke_token(cls, token: str) -> None:
        """删除令牌。"""
        await redis.delete(cls._token_key(token))
