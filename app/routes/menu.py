from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import json

from app.core.db import get_db
from app.core.redis import redis_client
from app.schemas.company import CompanyResponse
from app.schemas.category import CategoryResponse
from app.schemas.product import ProductResponse
from app.models.company import Company
from app.models.category import Category
from app.models.products import Product
from app.services import product_service

router = APIRouter()


async def get_active_company(
    company_id: int,
    db: AsyncSession = Depends(get_db)
) -> Company:
    result = await db.execute(select(Company).filter(Company.id == company_id))
    company = result.scalar_one_or_none()

    if not company or not company.status:
        raise HTTPException(status_code=404, detail="Company not found")

    return company


# COMPANY INFO
@router.get("/menu/{company_id}", response_model=CompanyResponse)
async def get_public_company_info(company: Company = Depends(get_active_company)):
    return company


# CATEGORIES (CACHE)
@router.get("/menu/{company_id}/categories", response_model=List[CategoryResponse])
async def get_categories(
    company: Company = Depends(get_active_company),
    db: AsyncSession = Depends(get_db)
):
    cache_key = f"categories:{company.id}"

    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    result = await db.execute(
        select(Category).filter(
            Category.company_id == company.id,
            Category.status == True
        )
    )
    categories = result.scalars().all()

    data = [CategoryResponse.model_validate(c).model_dump() for c in categories]

    await redis_client.set(cache_key, json.dumps(data), ex=120)

    return data


@router.get("/menu/{company_id}/products", response_model=List[ProductResponse])
async def get_products(
    company: Company = Depends(get_active_company),
    db: AsyncSession = Depends(get_db)
):
    cache_key = f"products:{company.id}"

    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    result = await db.execute(
        select(Product).filter(
            Product.company_id == company.id,
            Product.status == True,
            Product.is_available == True
        )
    )
    products = result.scalars().all()

    data = [ProductResponse.model_validate(p).model_dump() for p in products]

    await redis_client.set(cache_key, json.dumps(data), ex=60)

    return data


@router.get("/menu/{company_id}/search")
async def search_products(
    company_id: int,
    q: str = Query(..., min_length=1),
    limit: int = 10,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    cache_key = f"search:{company_id}:{q}:{limit}:{offset}"

    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    similarity_threshold = 0.2

    query = (
        select(Product)
        .where(
            Product.company_id == company_id,
            Product.status == True,
            Product.is_available == True,
            func.similarity(Product.title, q) > similarity_threshold
        )
        .order_by(func.similarity(Product.title, q).desc())
        .limit(limit)
        .offset(offset)
    )

    result = await db.execute(query)
    products = result.scalars().all()

    data = [ProductResponse.model_validate(p).model_dump() for p in products]

    await redis_client.set(cache_key, json.dumps(data), ex=30)

    return data