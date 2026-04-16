from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.security import AccessTokenService
from app.services.user_service import UserService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/login')


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    username = await AccessTokenService.get_subject(token)
    if not username:
        raise credentials_exception

    user = await UserService.get_user(username)
    if not user:
        raise credentials_exception
    return user
