from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.security import check_role, get_current_user_token
from app.core.enums import UserRole
from app.schemas.company import CompanyProfileUpdate, CompanyResponse
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.services import company_service, category_service, product_service
from app.models.user import User

router = APIRouter(dependencies=[Depends(check_role([UserRole.COMPANY]))])

@router.get("/profile", response_model=CompanyResponse)
async def get_company_profile_route(
        current_user: User = Depends(get_current_user_token)
):
    return current_user.company

@router.put("/profile", response_model=CompanyResponse)
async def update_company_profile_route(
        request: CompanyProfileUpdate,
        current_user: User = Depends(get_current_user_token),
        db: AsyncSession = Depends(get_db)
):
    return await company_service.update_company_profile(current_user.company.id, request, db)

@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category_route(
        request: CategoryCreate,
        current_user: User = Depends(get_current_user_token),
        db: AsyncSession = Depends(get_db)
):
    return await category_service.create_category(current_user.company.id, request, db)

@router.get("/categories", response_model=List[CategoryResponse])
async def get_company_categories_route(
        current_user: User = Depends(get_current_user_token),
        db: AsyncSession = Depends(get_db)
):
    return await category_service.get_categories(current_user.company.id, db)

@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_company_category_route(
        category_id: int,
        request: CategoryUpdate,
        current_user: User = Depends(get_current_user_token),
        db: AsyncSession = Depends(get_db)
):
    return await category_service.update_category(category_id, current_user.company.id, request, db)

@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company_category_route(
        category_id: int,
        current_user: User = Depends(get_current_user_token),
        db: AsyncSession = Depends(get_db)
):
    await category_service.delete_category(category_id, current_user.company.id, db)
    return

@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product_route(
        request: ProductCreate,
        current_user: User = Depends(get_current_user_token),
        db: AsyncSession = Depends(get_db)
):
    return await product_service.create_product(current_user.company.id, request, db)

@router.get("/products", response_model=List[ProductResponse])
async def get_company_products_route(
        current_user: User = Depends(get_current_user_token),
        db: AsyncSession = Depends(get_db)
):
    return await product_service.get_products(current_user.company.id, db)

@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_company_product_route(
        product_id: int,
        request: ProductUpdate,
        current_user: User = Depends(get_current_user_token),
        db: AsyncSession = Depends(get_db)
):
    return await product_service.update_product(product_id, current_user.company.id, request, db)

@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company_product_route(
        product_id: int,
        current_user: User = Depends(get_current_user_token),
        db: AsyncSession = Depends(get_db)
):
    await product_service.delete_product(product_id, current_user.company.id, db)
    return