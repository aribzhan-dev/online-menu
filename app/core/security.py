from datetime import datetime, timedelta, timezone
from typing import List

from fastapi.security import HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Security, Header
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import selectinload

from app.core.db import get_db
from app.core.config import settings
from app.core.enums import UserRole
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

security = HTTPBearer()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_token(data: dict, expires_delta: timedelta, token_type: str = "access") -> str:
    to_encode = data.copy()
    to_encode.update({
        "exp": datetime.now(timezone.utc) + expires_delta,
        "type": token_type
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(data: dict) -> str:
    expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_token(data, expires, "access")


def create_refresh_token(data: dict) -> str:
    expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return create_token(data, expires, "refresh")


def decode_token(token: str):
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None


async def get_current_user_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: AsyncSession = Depends(get_db)
):
    token = credentials.credentials

    payload = decode_token(token)

    if payload is None or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")

    if payload.get("role") == UserRole.ADMIN.value:
        return {"id": "admin", "role": UserRole.ADMIN.value}

    result = await db.execute(
        select(User).options(selectinload(User.company)).where(User.id == int(user_id))
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def check_role(required_roles: List[UserRole]):
    def role_checker(current_user=Depends(get_current_user_token)):

        if isinstance(current_user, dict):
            user_role = current_user.get("role")
        else:
            user_role = current_user.role

        if user_role not in [role.value for role in required_roles]:
            raise HTTPException(
                status_code=403,
                detail="Not authorized"
            )

        return current_user

    return role_checker