from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.db_models import UserDB


class UserService:
    @staticmethod
    async def init_admin(session: AsyncSession) -> None:
        result = await session.execute(select(UserDB).where(UserDB.username == 'admin'))
        if result.scalar_one_or_none():
            return

        admin = UserDB(
            username='admin',
            password_hash=get_password_hash('admin123!'),
            is_active=True,
            is_admin=True,
        )
        session.add(admin)
        await session.commit()

    @staticmethod
    async def get_user(session: AsyncSession, username: str) -> dict | None:
        result = await session.execute(select(UserDB).where(UserDB.username == username))
        user = result.scalar_one_or_none()
        if not user:
            return None
        return {
            'username': user.username,
            'password_hash': user.password_hash,
            'is_active': user.is_active,
            'is_admin': user.is_admin,
        }

    @staticmethod
    async def list_users(session: AsyncSession) -> list[dict]:
        result = await session.execute(select(UserDB).order_by(UserDB.id.asc()))
        users = result.scalars().all()
        return [
            {
                'username': user.username,
                'is_active': user.is_active,
                'is_admin': user.is_admin,
                'created_at': user.created_at,
            }
            for user in users
        ]

    @staticmethod
    async def upsert_user(session: AsyncSession, username: str, password: str, is_admin: bool = False) -> None:
        result = await session.execute(select(UserDB).where(UserDB.username == username))
        user = result.scalar_one_or_none()
        if user:
            user.password_hash = get_password_hash(password)
            user.is_admin = is_admin
            user.is_active = True
        else:
            user = UserDB(
                username=username,
                password_hash=get_password_hash(password),
                is_active=True,
                is_admin=is_admin,
            )
            session.add(user)
        await session.commit()

    @staticmethod
    async def update_user(session: AsyncSession, username: str, password: str | None, is_active: bool | None, is_admin: bool | None) -> bool:
        result = await session.execute(select(UserDB).where(UserDB.username == username))
        user = result.scalar_one_or_none()
        if not user:
            return False
        if password:
            user.password_hash = get_password_hash(password)
        if is_active is not None:
            user.is_active = is_active
        if is_admin is not None:
            user.is_admin = is_admin
        await session.commit()
        return True

    @staticmethod
    async def delete_user(session: AsyncSession, username: str) -> bool:
        result = await session.execute(select(UserDB).where(UserDB.username == username))
        user = result.scalar_one_or_none()
        if not user:
            return False
        await session.delete(user)
        await session.commit()
        return True
