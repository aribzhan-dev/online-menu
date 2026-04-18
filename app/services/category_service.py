from typing import List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.category import Category
from app.models.company import Company
from app.schemas.category import CategoryCreate, CategoryUpdate


async def _get_company_category(category_id: int, company_id: int, db: AsyncSession) -> Category:
    result = await db.execute(
        select(Category).filter(Category.id == category_id, Category.company_id == company_id)
    )
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found or does not belong to the company")
    return category


async def create_category(company_id: int, data: CategoryCreate, db: AsyncSession) -> Category:
    result = await db.execute(select(Company).filter(Company.id == company_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    new_category = Category(company_id=company_id, **data.model_dump())
    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)
    return new_category


async def get_categories(company_id: int, db: AsyncSession) -> List[Category]:
    result = await db.execute(select(Category).filter(Category.company_id == company_id))
    return result.scalars().all()


async def get_category(category_id: int, company_id: int, db: AsyncSession) -> Category:
    return await _get_company_category(category_id, company_id, db)


async def update_category(category_id: int, company_id: int, data: CategoryUpdate, db: AsyncSession) -> Category:
    category = await _get_company_category(category_id, company_id, db)
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)
    await db.commit()
    await db.refresh(category)
    return category


async def delete_category(category_id: int, company_id: int, db: AsyncSession):
    category = await _get_company_category(category_id, company_id, db)
    await db.delete(category)
    await db.commit()
    return {"message": "Category deleted successfully"}