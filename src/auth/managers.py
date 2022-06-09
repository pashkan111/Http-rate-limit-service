from typing import Optional
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func

from .models import AuthUser, Token
from .services import get_password_hash, create_token


class BaseManager:
    """
    Базовый менеджер моделей
    """
    def __init__(self, db_session: AsyncSession):
        self.session = db_session


class AuthManager(BaseManager):
    @classmethod
    async def create_user(cls, session: AsyncSession, data: AuthUser) -> Optional[str]:
        """
        Создаем нового пользователя и токен
        """
        session.begin()
        try:
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
        except Exception:
            await session.rollback()
            
    
    @classmethod
    async def authenticate_user(cls, session: AsyncSession, token: str) -> bool:
        command = select(Token).where(Token.user_token==token).with_only_columns([func.count()])
        token_count = await session.execute(command)
        if token_count.scalar() == 1:
            return True
        return False
