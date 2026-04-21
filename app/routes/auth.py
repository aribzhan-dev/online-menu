from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import LoginRequest, Token, RefreshRequest, AccessToken
from app.services import auth_service
from app.core.db import get_db
from app.core.security import get_current_user_token
from app.core.limiter import limiter

router = APIRouter()



@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login_route(
    request: Request,
    data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        return await auth_service.login(data, db)
    except Exception:
        raise HTTPException(401, "Invalid credentials")



@router.post("/refresh", response_model=AccessToken)
@limiter.limit("10/minute")
async def refresh_route(
    request: Request,
    data: RefreshRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        return await auth_service.refresh_access_token(data, db)
    except Exception:
        raise HTTPException(401, "Invalid refresh token")


@router.get("/me")
@limiter.limit("30/minute")
async def get_me(
    request: Request,
    user=Depends(get_current_user_token)
):
    return user