from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from db import get_session
from .managers import AuthManager
from .auth_backend import check_user
from .schemas import AuthUserSchema


router = APIRouter()


@router.post('/register')
async def register(data: AuthUserSchema, session: AsyncSession = Depends(get_session)):
    token = await AuthManager.create_user(session, data)
    return {'token': token}


@router.get('/show_date', dependencies=[Depends(check_user)])
async def test_route():
    """Тестовый роут"""
    datetime_now = datetime.now()
    return {
        'year': datetime_now.year,
        'month': datetime_now.month,
        'day': datetime_now.day,
    }