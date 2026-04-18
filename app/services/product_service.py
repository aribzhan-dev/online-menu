from typing import List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.products import Product
from app.models.category import Category
from app.schemas.product import ProductCreate, ProductUpdate


async def _get_company_product(product_id: int, company_id: int, db: AsyncSession) -> Product:
    result = await db.execute(
        select(Product).filter(Product.id == product_id, Product.company_id == company_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Product not found or does not belong to the company")
    return product


async def create_product(company_id: int, data: ProductCreate, db: AsyncSession) -> Product:
    result = await db.execute(
        select(Category).filter(Category.id == data.category_id, Category.company_id == company_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Category not found or does not belong to this company")

    new_product = Product(company_id=company_id, **data.model_dump())
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product


async def get_products(company_id: int, db: AsyncSession) -> List[Product]:
    result = await db.execute(select(Product).filter(Product.company_id == company_id))
    return result.scalars().all()


async def get_product(product_id: int, company_id: int, db: AsyncSession) -> Product:
    return await _get_company_product(product_id, company_id, db)


async def update_product(product_id: int, company_id: int, data: ProductUpdate, db: AsyncSession) -> Product:
    product = await _get_company_product(product_id, company_id, db)

    if data.category_id:
        result = await db.execute(
            select(Category).filter(Category.id == data.category_id, Category.company_id == company_id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="New category not found or does not belong to this company")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)
    await db.commit()
    await db.refresh(product)
    return product


async def delete_product(product_id: int, company_id: int, db: AsyncSession):
    product = await _get_company_product(product_id, company_id, db)
    await db.delete(product)
    await db.commit()
    return {"message": "Product deleted successfully"}


async def get_products_by_tag(company_id: int, tag: str, db: AsyncSession) -> List[Product]:
    valid_tags = {"new": Product.is_new, "popular": Product.is_popular, "chef_recommended": Product.is_chef_recommended}
    if tag not in valid_tags:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid tag specified. Must be 'new', 'popular', or 'chef_recommended'.")

    result = await db.execute(
        select(Product).filter(Product.company_id == company_id, valid_tags[tag].is_(True))
    )
    return result.scalars().all()