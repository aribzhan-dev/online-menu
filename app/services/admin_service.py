from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.password import validate_new_password
from app.core.security import hash_password, verify_password
from app.models.company import Company
from app.models.user import User


async def reset_company_password(company_id: int, new_password: str, db: AsyncSession):
    result = await db.execute(
        select(User)
        .join(Company, Company.user_id == User.id)
        .where(Company.id == company_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )

    if verify_password(new_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )

    validate_new_password(new_password, login=user.login)

    user.hashed_password = hash_password(new_password)
    user.token_version += 1

    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    return {
        "message": "Password reset successfully. Old tokens are now invalid."
    }