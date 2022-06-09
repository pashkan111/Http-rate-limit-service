from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_session
from .managers import AuthManager
from .models import AuthUser


router = APIRouter()


@router.post('/register')
async def register(data: AuthUser, session: AsyncSession = Depends(get_session)):
    token = await AuthManager.create_user(session, data)
    return {'token': token}
