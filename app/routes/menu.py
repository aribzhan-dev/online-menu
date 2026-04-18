from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.core.db import get_db
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found or is inactive")
    return company

@router.get("/{company_id}", response_model=CompanyResponse)
async def get_public_company_info(
        company: Company = Depends(get_active_company)
):
    return company

@router.get("/{company_id}/categories", response_model=List[CategoryResponse])
async def get_public_company_categories(
        company: Company = Depends(get_active_company),
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Category).filter(Category.company_id == company.id, Category.status == True))
    return result.scalars().all()

@router.get("/{company_id}/products", response_model=List[ProductResponse])
async def get_public_company_products(
        company: Company = Depends(get_active_company),
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Product).filter(
        Product.company_id == company.id, Product.status == True, Product.is_available == True
    ))
    return result.scalars().all()

@router.get("/{company_id}/products/tag/{tag}", response_model=List[ProductResponse])
async def get_public_products_by_tag(
        tag: str,
        company: Company = Depends(get_active_company),
        db: AsyncSession = Depends(get_db)
):
    products = await product_service.get_products_by_tag(company.id, tag, db)
    return [p for p in products if p.status and p.is_available]


@router.get("/{company_id}/search")
async def search_products(
    company_id: int,
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    query = select(Product).where(
        Product.company_id == company_id,
        or_(
            Product.title.ilike(f"%{q}%"),
            Product.description.ilike(f"%{q}%")
        )
    )
    query = query.limit(limit).offset(offset)


    result = await db.execute(query)
    products = result.scalars().all()

    return {
        "count": len(products),
        "limit": limit,
        "offset": offset,
        "results": products
    }