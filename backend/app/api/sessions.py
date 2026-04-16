from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db import get_db_session
from app.services.session_service import SessionService

router = APIRouter(prefix='/sessions', tags=['sessions'])


@router.get('')
async def list_sessions(_: dict = Depends(get_current_user)) -> list[dict]:
    return await SessionService.list_sessions()


@router.delete('/{session_id}')
async def force_offline(
    session_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    await SessionService.terminate_session(session_id, actor=user['username'], db=db)
    return {'ok': True}
