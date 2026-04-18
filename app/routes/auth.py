from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import LoginRequest, Token, RefreshRequest, AccessToken
from app.services import auth_service
from app.core.db import get_db
from app.core.security import get_current_user_token

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_route(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    return await auth_service.login(request, db)


@router.post("/refresh", response_model=AccessToken)
async def refresh_route(
    request: RefreshRequest,
    db: AsyncSession = Depends(get_db)
):
    return await auth_service.refresh_access_token(request, db)


@router.get("/me")
async def get_me(user=Depends(get_current_user_token)):
    return user