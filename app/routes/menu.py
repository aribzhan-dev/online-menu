from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.cache import get_cache, set_cache
from app.models.category import Category
from app.models.company import Company
from app.models.products import Product
from app.schemas.category import CategoryResponse
from app.schemas.company import CompanyResponse
from app.schemas.product import ProductResponse
from app.services import product_service

router = APIRouter()


async def get_active_company(company_id: int, db: AsyncSession = Depends(get_db)) -> Company:
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()

    if not company or not company.status:
        raise HTTPException(404, "Company not found")

    return company


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(company: Company = Depends(get_active_company)):
    return company


@router.get("/{company_id}/categories", response_model=List[CategoryResponse])
async def get_categories(company: Company = Depends(get_active_company), db: AsyncSession = Depends(get_db)):

    cache_key = f"categories:{company.id}"

    cached = await get_cache(cache_key)
    if cached:
        return cached

    result = await db.execute(
        select(Category).where(
            Category.company_id == company.id,
            Category.status.is_(True)
        )
    )

    categories = result.scalars().all()

    data = [
        CategoryResponse.model_validate(c).model_dump(mode="json")
        for c in categories
    ]

    await set_cache(cache_key, data, 120)

    return data


@router.get("/{company_id}/products", response_model=List[ProductResponse])
async def get_products(company: Company = Depends(get_active_company), db: AsyncSession = Depends(get_db)):

    cache_key = f"products:{company.id}"

    cached = await get_cache(cache_key)
    if cached:
        return cached

    result = await db.execute(
        select(Product).where(
            Product.company_id == company.id,
            Product.status.is_(True),
            Product.is_available.is_(True)
        )
    )

    products = result.scalars().all()

    data = [
        ProductResponse.model_validate(p).model_dump(mode="json")
        for p in products
    ]

    await set_cache(cache_key, data, 60)

    return data


@router.get("/{company_id}/search", response_model=List[ProductResponse])
async def search_products(
    company: Company = Depends(get_active_company),
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):

    cache_key = f"search:{company.id}:{q}"

    cached = await get_cache(cache_key)
    if cached:
        return cached

    query = (
        select(Product)
        .where(
            Product.company_id == company.id,
            Product.status.is_(True),
            Product.is_available.is_(True),
            func.similarity(Product.title, q) > 0.2
        )
        .order_by(func.similarity(Product.title, q).desc())
        .limit(10)
    )

    result = await db.execute(query)
    products = result.scalars().all()

    data = [
        ProductResponse.model_validate(p).model_dump(mode="json")
        for p in products
    ]

    await set_cache(cache_key, data, 30)

    return data