from typing import List
import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.redis import redis_client
from app.models.category import Category
from app.models.company import Company
from app.models.products import Product
from app.schemas.category import CategoryResponse
from app.schemas.company import CompanyResponse
from app.schemas.product import ProductResponse
from app.services import product_service

router = APIRouter()


async def get_active_company(
    company_id: int,
    db: AsyncSession = Depends(get_db),
) -> Company:
    result = await db.execute(
        select(Company).where(Company.id == company_id)
    )
    company = result.scalar_one_or_none()

    if not company or not company.status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found or is inactive",
        )

    return company


async def _get_cached_json(key: str):
    try:
        cached = await redis_client.get(key)
        if cached:
            return json.loads(cached)
    except Exception as e:
        print("Redis GET error:", e)
    return None


async def _set_cached_json(key: str, data, expire_seconds: int):
    try:
        await redis_client.set(
            key,
            json.dumps(jsonable_encoder(data), ensure_ascii=False),
            ex=expire_seconds,
        )
    except Exception as e:
        print("Redis SET error:", e)


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_public_company_info(
    company: Company = Depends(get_active_company),
):
    return company


@router.get("/{company_id}/categories", response_model=List[CategoryResponse])
async def get_categories(
    company: Company = Depends(get_active_company),
    db: AsyncSession = Depends(get_db),
):
    cache_key = f"categories:{company.id}"

    cached = await _get_cached_json(cache_key)
    if cached is not None:
        return cached

    result = await db.execute(
        select(Category).where(
            Category.company_id == company.id,
            Category.status.is_(True),
        )
    )
    categories = result.scalars().all()

    data = [CategoryResponse.model_validate(c).model_dump(mode="json") for c in categories]
    await _set_cached_json(cache_key, data, expire_seconds=120)

    return data


@router.get("/{company_id}/products", response_model=List[ProductResponse])
async def get_products(
    company: Company = Depends(get_active_company),
    db: AsyncSession = Depends(get_db),
):
    cache_key = f"products:{company.id}"

    cached = await _get_cached_json(cache_key)
    if cached is not None:
        return cached

    result = await db.execute(
        select(Product).where(
            Product.company_id == company.id,
            Product.status.is_(True),
            Product.is_available.is_(True),
        )
    )
    products = result.scalars().all()

    data = [ProductResponse.model_validate(p).model_dump(mode="json") for p in products]
    await _set_cached_json(cache_key, data, expire_seconds=60)

    return data


@router.get("/{company_id}/products/tag/{tag}", response_model=List[ProductResponse])
async def get_public_products_by_tag(
    tag: str,
    company: Company = Depends(get_active_company),
    db: AsyncSession = Depends(get_db),
):
    cache_key = f"products_tag:{company.id}:{tag}"

    cached = await _get_cached_json(cache_key)
    if cached is not None:
        return cached

    products = await product_service.get_products_by_tag(company.id, tag, db)
    data = [ProductResponse.model_validate(p).model_dump(mode="json") for p in products]

    await _set_cached_json(cache_key, data, expire_seconds=60)
    return data


@router.get("/{company_id}/search", response_model=List[ProductResponse])
async def search_products(
    company: Company = Depends(get_active_company),
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    cache_key = f"search:{company.id}:{q}:{limit}:{offset}"

    cached = await _get_cached_json(cache_key)
    if cached is not None:
        return cached

    similarity_threshold = 0.2

    query = (
        select(Product)
        .where(
            Product.company_id == company.id,
            Product.status.is_(True),
            Product.is_available.is_(True),
            func.similarity(Product.title, q) > similarity_threshold,
        )
        .order_by(func.similarity(Product.title, q).desc())
        .limit(limit)
        .offset(offset)
    )

    result = await db.execute(query)
    products = result.scalars().all()

    data = [ProductResponse.model_validate(p).model_dump(mode="json") for p in products]
    await _set_cached_json(cache_key, data, expire_seconds=30)

    return data