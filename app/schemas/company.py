from datetime import datetime, time
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class CompanyCreateRequest(BaseModel):
    name: str
    login: str
    password: str
    description: Optional[str] = None
    logo: Optional[str] = None


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    logo: Optional[str] = None
    status: Optional[bool] = None


class CompanyProfileUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    logo: Optional[str] = None
    wifi_name: Optional[str] = None
    wifi_password: Optional[str] = None
    opening_time: Optional[time] = None
    closing_time: Optional[time] = None


class CompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    logo: Optional[str] = None
    description: Optional[str] = None
    wifi_name : Optional[str] = None
    wifi_password: Optional[str] = None
    opening_time: Optional[time] = None
    closing_time: Optional[time] = None
    status: bool
    created_at: datetime
    updated_at: datetime


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)


class ResetPasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=6)