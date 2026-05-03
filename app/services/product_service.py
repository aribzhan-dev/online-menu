from typing import List

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.redis import redis_client
from app.models.category import Category
from app.models.products import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.core.cache import clear_product_cache
from app.core.logger import get_logger

logger = get_logger(__name__)




async def _get_company_product(
    product_id: int,
    company_id: int,
    db: AsyncSession,
) -> Product:
    result = await db.execute(
        select(Product)
        .options(selectinload(Product.category))  # 🔥 FIX
        .where(
            Product.id == product_id,
            Product.company_id == company_id,
        )
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or does not belong to the company",
        )

    return product


async def _validate_category_belongs_to_company(
    category_id: int,
    company_id: int,
    db: AsyncSession,
) -> None:
    result = await db.execute(
        select(Category).where(
            Category.id == category_id,
            Category.company_id == company_id,
        )
    )
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category not found or does not belong to this company",
        )



async def create_product(
    company_id: int,
    data: ProductCreate,
    db: AsyncSession,
) -> Product:
    await _validate_category_belongs_to_company(data.category_id, company_id, db)

    logger.info(f"Creating product '{data.title}' for company {company_id}")

    new_product = Product(
        company_id=company_id,
        **data.model_dump(),
    )

    db.add(new_product)

    try:
        await db.commit()
        await db.refresh(new_product)
        logger.info(f"Product created successfully: ID={new_product.id}")
    except IntegrityError as e:
        await db.rollback()
        logger.error(f"Integrity error creating product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product with this name already exists"
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating product: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create product"
        )

    await clear_product_cache(company_id)

    return new_product


async def get_products(company_id: int, db: AsyncSession) -> List[Product]:
    result = await db.execute(
        select(Product)
        .options(selectinload(Product.category))  # 🔥 FIX
        .where(Product.company_id == company_id)
    )
    return result.scalars().all()


async def get_product(
    product_id: int,
    company_id: int,
    db: AsyncSession,
) -> Product:
    return await _get_company_product(product_id, company_id, db)


async def update_product(
    product_id: int,
    company_id: int,
    data: ProductUpdate,
    db: AsyncSession,
) -> Product:
    product = await _get_company_product(product_id, company_id, db)

    if data.category_id is not None:
        await _validate_category_belongs_to_company(data.category_id, company_id, db)

    update_data = data.model_dump(exclude_unset=True)

    logger.info(f"Updating product {product_id} for company {company_id}")

    for key, value in update_data.items():
        setattr(product, key, value)

    try:
        await db.commit()
        await db.refresh(product)
        logger.info(f"Product {product_id} updated successfully")
    except IntegrityError as e:
        await db.rollback()
        logger.error(f"Integrity error updating product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product update violates constraints"
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating product: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update product"
        )

    await clear_product_cache(company_id)

    return product


async def delete_product(
    product_id: int,
    company_id: int,
    db: AsyncSession,
):
    product = await _get_company_product(product_id, company_id, db)

    logger.info(f"Deleting product {product_id} for company {company_id}")

    await db.delete(product)

    try:
        await db.commit()
        logger.info(f"Product {product_id} deleted successfully")
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting product: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete product"
        )

    await clear_product_cache(company_id)

    return {"message": "Product deleted successfully"}



async def get_products_by_tag(
    company_id: int,
    tag: str,
    db: AsyncSession,
) -> List[Product]:
    valid_tags = {
        "new": Product.is_new,
        "popular": Product.is_popular,
        "chef_recommended": Product.is_chef_recommended,
    }

    if tag not in valid_tags:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tag",
        )

    result = await db.execute(
        select(Product)
        .options(selectinload(Product.category))
        .where(
            Product.company_id == company_id,
            Product.status.is_(True),
            Product.is_available.is_(True),
            valid_tags[tag].is_(True),
        )
    )
    return result.scalars().all()