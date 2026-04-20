from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.enums import UserRole
from app.core.security import check_role
from app.schemas.company import CompanyCreateRequest, CompanyUpdate, CompanyResponse, ResetPasswordRequest
from app.services import company_service, admin_service

router = APIRouter(dependencies=[Depends(check_role([UserRole.ADMIN]))])


@router.post("/companies", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company_route(
    request: CompanyCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    return await company_service.create_company(request, db)


@router.get("/companies", response_model=List[CompanyResponse])
async def get_all_companies_route(
    db: AsyncSession = Depends(get_db)
):
    return await company_service.get_companies(db)


@router.get("/companies/{company_id}", response_model=CompanyResponse)
async def get_company_by_id_route(
    company_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await company_service.get_company(company_id, db)


@router.put("/companies/{company_id}", response_model=CompanyResponse)
async def update_company_by_id_route(
    company_id: int,
    request: CompanyUpdate,
    db: AsyncSession = Depends(get_db)
):
    return await company_service.update_company(company_id, request, db)


@router.put("/companies/{company_id}/reset-password")
async def reset_company_password_route(
    company_id: int,
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    return await admin_service.reset_company_password(
        company_id=company_id,
        new_password=request.new_password,
        db=db
    )


@router.delete("/companies/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company_by_id_route(
    company_id: int,
    db: AsyncSession = Depends(get_db)
):
    await company_service.delete_company(company_id, db)
    return