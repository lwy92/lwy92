from datetime import timedelta

from fastapi import APIRouter, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings
from app.core.security import AccessTokenService, verify_password
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.user_service import UserService
from app.services.session_service import SessionService
from app.utils.ip import get_client_ip

router = APIRouter(prefix='/auth', tags=['auth'])
limiter = Limiter(key_func=get_remote_address)


@router.post('/login', response_model=TokenResponse)
@limiter.limit(settings.login_rate_limit)
async def login(request: Request, payload: LoginRequest) -> TokenResponse:
    user = await UserService.get_user(payload.username)
    if not user or not verify_password(payload.password, user['password_hash']):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid username or password')

    ip = get_client_ip(request)
    session_id, _ = await SessionService.create_session(user['username'], ip, payload.ports)
    token = await AccessTokenService.create_access_token(
        subject=user['username'],
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return TokenResponse(access_token=token, session_id=session_id, ip=ip)


@router.post('/logout/{session_id}')
async def logout(session_id: str) -> dict:
    await SessionService.terminate_session(session_id, actor='user')
    return {'ok': True}
