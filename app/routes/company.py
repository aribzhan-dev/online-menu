from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import get_cache, set_cache, clear_company_cache
from app.core.db import get_db
from app.core.enums import UserRole
from app.core.security import check_role, get_current_user_token
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.schemas.company import CompanyResponse, CompanyProfileUpdate, ChangePasswordRequest
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.services import company_service, category_service, product_service

router = APIRouter(dependencies=[Depends(check_role([UserRole.COMPANY]))])


@router.get("/profile", response_model=CompanyResponse)
async def get_profile(current_user: User = Depends(get_current_user_token)):
    company_id = current_user.company.id
    cache_key = f"company:{company_id}"

    cached = await get_cache(cache_key)
    if cached:
        return cached

    data = CompanyResponse.model_validate(current_user.company).model_dump(mode="json")
    await set_cache(cache_key, data, 120)

    return data


@router.put("/profile", response_model=CompanyResponse)
async def update_profile(
    request: CompanyProfileUpdate,
    current_user: User = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    company = await company_service.update_company_profile(
        current_user.company.id,
        request,
        db,
        current_user
    )

    await clear_company_cache(current_user.company.id)
    return company


@router.put("/change-password")
async def change_password_route(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    return await company_service.change_password(
        current_user=current_user,
        old_password=request.old_password,
        new_password=request.new_password,
        db=db
    )


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    request: CategoryCreate,
    current_user: User = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    category = await category_service.create_category(current_user.company.id, request, db)
    await clear_company_cache(current_user.company.id)
    return category


@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(
    current_user: User = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    return await category_service.get_categories(current_user.company.id, db)


@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    request: CategoryUpdate,
    current_user: User = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    category = await category_service.update_category(
        category_id,
        current_user.company.id,
        request,
        db
    )

    await clear_company_cache(current_user.company.id)
    return category


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    await category_service.delete_category(category_id, current_user.company.id, db)
    await clear_company_cache(current_user.company.id)
    return


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    request: ProductCreate,
    current_user: User = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    return await product_service.create_product(current_user.company.id, request, db)


@router.get("/products", response_model=List[ProductResponse])
async def get_company_products(
    current_user: User = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    products = await product_service.get_products(
        current_user.company.id,
        db
    )
    return [
        ProductResponse.model_validate(p)
        for p in products
    ]


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    request: ProductUpdate,
    current_user: User = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    return await product_service.update_product(
        product_id,
        current_user.company.id,
        request,
        db
    )


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db)
):
    await product_service.delete_product(product_id, current_user.company.id, db)
    return