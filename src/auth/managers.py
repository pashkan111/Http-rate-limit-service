from typing import Optional
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from fastapi.exceptions import HTTPException
from fastapi import status

from .models import AuthUser, Token
from .services import get_password_hash, create_token
from .schemas import AuthUserSchema
from .exceptions import BadDataException


class AuthManager:
    """
    Класс отвечает за регистрацию и аутентификацию пользователей
    """
    
    @classmethod
    async def check_login(cls, session: AsyncSession, login: str) -> Optional[bool]:
        command = select(AuthUser).where(AuthUser.login==login).with_only_columns([func.count()])
        user_count = await session.execute(command)
        if user_count.scalar() == 1:
            raise BadDataException
        return True
            
    @classmethod
    async def create_user(cls, session: AsyncSession, data: AuthUserSchema) -> Optional[str]:
        """
        Создаем нового пользователя и токен
        """
        session.begin()
        try:
            await cls.check_login(session, data.login)
            hashed_password = get_password_hash(data.password)
            new_user = AuthUser(
                login=data.login, password=hashed_password
            )
            session.add(new_user)
            await session.commit()
            
            user_token = create_token()
            new_token = Token(
                user_token=user_token, user_id=new_user.id
            )
            session.add(new_token)
            await session.commit()
            return user_token
        except BadDataException:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail='User with such login already exists'
                )
        except Exception:
            await session.rollback()
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Something went wrong'
                )
    
    @classmethod
    async def authenticate_user(cls, session: AsyncSession, token: str) -> bool:
        command = select(Token).where(Token.user_token==token).with_only_columns([func.count()])
        token_count = await session.execute(command)
        if token_count.scalar() == 1:
            return True
        return False
