from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_session
from .managers import AuthManager
from .auth_backend import check_auth_user
from .models import AuthUser


router = APIRouter()


@router.post('/register')
async def register(data: AuthUser, response: Response, session: AsyncSession = Depends(get_session)):
    await AuthManager.create_user(session, data)
    response.status_code = status.HTTP_204_NO_CONTENT
