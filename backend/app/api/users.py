from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.deps import get_current_user
from app.services.user_service import UserService

router = APIRouter(prefix='/users', tags=['users'])


class UserCreate(BaseModel):
    username: str
    password: str
    is_admin: bool = False


@router.get('')
async def list_users(user: dict = Depends(get_current_user)) -> list[dict]:
    if not user['is_admin']:
        raise HTTPException(status_code=403, detail='Admin only')
    return await UserService.list_users()


@router.post('')
async def create_user(payload: UserCreate, user: dict = Depends(get_current_user)) -> dict:
    if not user['is_admin']:
        raise HTTPException(status_code=403, detail='Admin only')
    await UserService.upsert_user(payload.username, payload.password, payload.is_admin)
    return {'ok': True}
