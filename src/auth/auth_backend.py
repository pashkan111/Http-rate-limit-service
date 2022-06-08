from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from .managers import AuthManager
from db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
    
    
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def check_auth_user(
    token: str = Depends(oauth2_scheme), 
    session: AsyncSession = Depends(get_session)
    ) -> bool:
    """`
    Проверяет, авторизован ли пользователь
    """
    manager = AuthManager(session)
    is_authenticated = await manager.authenticate_user(token)
    return is_authenticated
    
    