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
    async def create_user(self, data: AuthUser):
        """
        Создаем нового пользователя и токен
        """
        self.session.begin()
        try:
            hashed_password = get_password_hash(data.password)
            new_user = AuthUser(
                login=data.login, password=hashed_password
            )
            self.session.add(new_user)
            await self.session.commit()
            
            user_token = create_token()
            new_token = Token(
                user_token=user_token, user_id=new_user.id
            )
            self.session.add(new_token)
            await self.session.commit()
        except:
            await self.session.rollback()
            
    async def authenticate_user(self, token: str) -> bool:
        command = select(Token).where(Token.user_token==token).with_only_columns([func.count()])
        token_count = await self.session.execute(command)
        if token_count.scalar() == 1:
            return True
        return False
