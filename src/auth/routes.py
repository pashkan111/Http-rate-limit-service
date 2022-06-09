from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from db import get_session
from .managers import AuthManager
from .models import AuthUser
from .auth_backend import check_user

router = APIRouter()


@router.post('/register')
async def register(data: AuthUser, session: AsyncSession = Depends(get_session)):
    token = await AuthManager.create_user(session, data)
    return {'token': token}


@router.get('/show_date', dependencies=[Depends(check_user)])
async def test_route():
    datetime_now = datetime.now()
    return {
        'year': datetime_now.year,
        'month': datetime_now.month,
        'day': datetime_now.day,
    }