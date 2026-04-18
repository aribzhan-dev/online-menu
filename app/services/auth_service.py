from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.core.security import (
    verify_password, create_access_token, create_refresh_token, decode_token, hash_password
)
from app.schemas.auth import Token, LoginRequest, RefreshRequest, AccessToken
from app.models.user import User
from app.core.enums import UserRole

async def login(data: LoginRequest, db: AsyncSession) -> Token:
    user = None
    if data.login == settings.ADMIN_LOGIN:
        if verify_password(data.password, settings.ADMIN_PASSWORD):
             user = {"id": "admin", "login": settings.ADMIN_LOGIN, "role": UserRole.ADMIN, "is_active": True}
    else:
        result = await db.execute(select(User).filter(User.login == data.login))
        db_user = result.scalar_one_or_none()
        if db_user and verify_password(data.password, db_user.hashed_password):
            user = db_user

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    is_active = user.is_active if hasattr(user, 'is_active') else user.get("is_active")
    if not is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

    user_id = user.id if hasattr(user, 'id') else user.get("id")
    user_role = user.role if hasattr(user, 'role') else user.get("role")

    token_data = {"sub": str(user_id), "role": user_role.value}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return Token(access_token=access_token, refresh_token=refresh_token)

async def refresh_access_token(data: RefreshRequest, db: AsyncSession) -> AccessToken:
    payload = decode_token(data.refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_id = payload.get("sub")
    user_role = payload.get("role")
    if not user_id or not user_role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    if user_role != UserRole.ADMIN.value:
        result = await db.execute(select(User).filter(User.id == int(user_id)))
        user = result.scalar_one_or_none()
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    new_access_token = create_access_token({"sub": user_id, "role": user_role})
    return AccessToken(access_token=new_access_token)