from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.enums import UserRole
from app.core.security import check_role
from app.schemas.company import CompanyCreateRequest, CompanyUpdate, CompanyResponse, ResetPasswordRequest
from app.services import company_service, admin_service

# 🔥 RATE LIMIT
from app.core.limiter import limiter

router = APIRouter(dependencies=[Depends(check_role([UserRole.ADMIN]))])



@router.post("/companies", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def create_company_route(
    request: Request,
    data: CompanyCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        return await company_service.create_company(data, db)
    except Exception:
        raise HTTPException(500, "Failed to create company")



@router.get("/companies", response_model=List[CompanyResponse])
@limiter.limit("30/minute")
async def get_all_companies_route(
    request: Request,
    limit: int = Query(20, le=100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db)
):
    try:
        companies = await company_service.get_companies(db)
        return companies[offset:offset + limit]
    except Exception:
        raise HTTPException(500, "Failed to fetch companies")



@router.get("/companies/{company_id}", response_model=CompanyResponse)
@limiter.limit("60/minute")
async def get_company_by_id_route(
    request: Request,
    company_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await company_service.get_company(company_id, db)



@router.put("/companies/{company_id}", response_model=CompanyResponse)
@limiter.limit("20/minute")
async def update_company_by_id_route(
    request: Request,
    company_id: int,
    data: CompanyUpdate,
    db: AsyncSession = Depends(get_db)
):
    return await company_service.update_company(company_id, data, db)



@router.put("/companies/{company_id}/reset-password")
@limiter.limit("5/minute")
async def reset_company_password_route(
    request: Request,
    company_id: int,
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    return await admin_service.reset_company_password(
        company_id=company_id,
        new_password=data.new_password,
        db=db
    )


@router.delete("/companies/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/minute")
async def delete_company_by_id_route(
    request: Request,
    company_id: int,
    db: AsyncSession = Depends(get_db)
):
    await company_service.delete_company(company_id, db)
    return {
        "status": "success",
        "message": "Successfully deleted company"
    }