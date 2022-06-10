from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .managers import AuthManager
from db import get_session, redis
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.requests import Request
from fastapi.security.utils import get_authorization_scheme_param
from typing import Optional
from fastapi.exceptions import HTTPException
import datetime
from .schemas import RedisMessageSchema
from .exceptions import RateLimitException


class CustomHTTPBearer(HTTPBearer):
    """
    Кастомный класс для получения токена авторизации
    """
    async def __call__(
        self, request: Request
    ) -> Optional[HTTPAuthorizationCredentials]:
        authorization: str = request.headers.get("Authorization")
        scheme, credentials = get_authorization_scheme_param(authorization)
        if (authorization and scheme and credentials):
            return HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)
        return None
        

bearer_scheme = CustomHTTPBearer()


class RequestCounter:
    """
    Класс, отвечающий за подсчет запросов для неавторизованных пользователей.
    В случае, если пользователь авторизован, то запросы не подсчитываются
    """
    format = "%d-%m-%y %H:%M:%S"
    max_count_queries = 60
    timeout_limit = 60
    
    async def count_requests(self, host: str) -> Optional[None]:
        """
        Основной метод для проверки и подсчета количества 
        запросов у пользователя
        """
        data = await redis.hgetall(host)
        if not data:
            bound_datetime = self._get_bound_datetime()
            message = self._create_data(bound_datetime)
            await redis.hset(
                host, 
                mapping=message.dict()
                )
            return
        data_validated = RedisMessageSchema(**data)
        print(data_validated.count)
        count = data_validated.count
        dt = datetime.datetime.strptime(data_validated.dt, self.format)
        now = datetime.datetime.now()
        difference = now - dt
        
        if count >= self.max_count_queries and difference <= datetime.timedelta(0):
            raise RateLimitException
        
        elif difference > datetime.timedelta(0):
            data_validated.count = 1
            data_validated.dt = self._get_bound_datetime()
            await redis.hset(
                host,
                mapping=data_validated.dict()
            )
            return

        incremented_count = count + 1
        data_validated.count = incremented_count
        await redis.hset(
            host,
            mapping=data_validated.dict()
        )
    
    def _get_bound_datetime(self) -> str:
        bound_datetime = datetime.datetime.now() + datetime.timedelta(seconds=self.timeout_limit)
        dt = bound_datetime.strftime(self.format)
        return dt
    
    def _create_data(
        self, 
        dt: str,
        count: int = 1
        ) -> RedisMessageSchema:
        schema = RedisMessageSchema(dt=dt, count=count)
        return schema


class UserManager:
    """
    Класс, отвечающий за аутентификацию пользователя
    """
    checker = RequestCounter()
    
    async def __call__(
        self, 
        request: Request,
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), 
        session: AsyncSession = Depends(get_session)
    ):
        if credentials is None:
            await self.process_request(request)
            return
        is_authenticated = await AuthManager.authenticate_user(session, credentials.credentials)
        if not is_authenticated:
            await self.process_request(request)
            return

    async def process_request(self, request: Request):
        host = self.get_host(request)
        try:
            await self.checker.count_requests(host)
        except RateLimitException:
            raise HTTPException(429)
    
    def get_host(self, request: Request) -> str:
        return request.client.host


check_user = UserManager()