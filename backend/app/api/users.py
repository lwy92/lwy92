from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db import get_db_session
from app.services.user_service import UserService
from app.services.user_session_log_service import UserSessionLogService

router = APIRouter(prefix='/users', tags=['users'])


class UserCreate(BaseModel):
    username: str
    password: str
    is_admin: bool = False


class UserUpdate(BaseModel):
    password: str | None = None
    is_active: bool | None = None
    is_admin: bool | None = None


def _ensure_admin(user: dict) -> None:
    if not user['is_admin']:
        raise HTTPException(status_code=403, detail='Admin only')


@router.get('')
async def list_users(user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db_session)) -> list[dict]:
    _ensure_admin(user)
    return await UserService.list_users(db)


@router.post('')
async def create_user(payload: UserCreate, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db_session)) -> dict:
    _ensure_admin(user)
    await UserService.upsert_user(db, payload.username, payload.password, payload.is_admin)
    return {'ok': True}


@router.patch('/{username}')
async def update_user(
    username: str,
    payload: UserUpdate,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    _ensure_admin(user)
    ok = await UserService.update_user(db, username, payload.password, payload.is_active, payload.is_admin)
    if not ok:
        raise HTTPException(status_code=404, detail='User not found')
    return {'ok': True}


@router.delete('/{username}')
async def delete_user(
    username: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    _ensure_admin(user)
    ok = await UserService.delete_user(db, username)
    if not ok:
        raise HTTPException(status_code=404, detail='User not found')
    return {'ok': True}


@router.get('/session-logs')
async def list_session_logs(
    username: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> list[dict]:
    _ensure_admin(user)
    return await UserSessionLogService.list_logs(db, username=username, limit=limit)
