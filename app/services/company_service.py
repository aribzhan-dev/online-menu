from typing import List

from fastapi import HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import UserRole
from app.core.password import validate_new_password
from app.core.security import hash_password, verify_password
from app.models.company import Company
from app.models.user import User
from app.schemas.company import CompanyCreateRequest, CompanyUpdate, CompanyProfileUpdate


async def create_company(data: CompanyCreateRequest, db: AsyncSession) -> Company:
    result = await db.execute(select(User).filter(User.login == data.login))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Login already registered"
        )

    validate_new_password(data.password, login=data.login)

    hashed_pw = hash_password(data.password)

    new_user = User(
        login=data.login,
        hashed_password=hashed_pw,
        role=UserRole.COMPANY
    )
    db.add(new_user)
    await db.flush()

    new_company = Company(
        user_id=new_user.id,
        name=data.name,
        logo=data.logo,
        description=data.description
    )
    db.add(new_company)

    try:
        await db.commit()
        await db.refresh(new_company)
    except Exception:
        await db.rollback()
        raise

    return new_company


async def get_companies(db: AsyncSession) -> List[Company]:
    result = await db.execute(select(Company))
    return result.scalars().all()


async def get_company(company_id: int, db: AsyncSession) -> Company:
    result = await db.execute(select(Company).filter(Company.id == company_id))
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )

    return company


async def update_company(company_id: int, data: CompanyUpdate, db: AsyncSession) -> Company:
    company = await get_company(company_id, db)
    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(company, key, value)

    try:
        await db.commit()
        await db.refresh(company)
    except Exception:
        await db.rollback()
        raise

    return company


async def update_company_profile(
    company_id: int,
    data: CompanyProfileUpdate,
    db: AsyncSession,
    current_user: User
) -> Company:
    if current_user.company.id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )

    company = await get_company(company_id, db)
    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(company, key, value)

    try:
        await db.commit()
        await db.refresh(company)
    except Exception:
        await db.rollback()
        raise

    return company


async def delete_company(company_id: int, db: AsyncSession):
    company = await get_company(company_id, db)

    await db.delete(company)

    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    return {"message": "Company and associated user deleted successfully"}


async def change_password(
    current_user: User,
    old_password: str,
    new_password: str,
    db: AsyncSession
):
    if not verify_password(old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect"
        )

    if old_password == new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from old password"
        )

    if verify_password(new_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )

    validate_new_password(new_password, login=current_user.login)

    current_user.hashed_password = hash_password(new_password)
    current_user.token_version += 1

    try:
        await db.commit()
        await db.refresh(current_user)
    except Exception:
        await db.rollback()
        raise

    return {
        "message": "Password changed successfully. Please login again."
    }