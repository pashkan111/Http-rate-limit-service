from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import AuthUser, Token
from .services import get_password_hash, create_token


class BaseManager:
    """
    Базовый менеджер моделей
    """
    def __init__(self, db_session: AsyncSession):
        self.session = db_session


class AuthManager(BaseManager):
    async def create_user(self, login: str, password: str):
        """
        Создаем нового пользователя и токен
        """
        async with self.session.begin():
            hashed_password = get_password_hash(password)
            new_user = AuthUser(
                login=login, password=hashed_password
            )
            self.session.add(new_user)
            await self.session.commit()
            
            user_token = create_token()
            new_token = Token(
                user_token=user_token, user_id=new_user.id
            )
            self.session.add(new_token)
            await self.session.commit()
            
    async def authenticate_user(self, token: str) -> bool:
        command = select(Token).where(Token.user_token==token).limit(1)
        user_token = await self.session.execute(command)
        if user_token is not None:
            return True
        return False
