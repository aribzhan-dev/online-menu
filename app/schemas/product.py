from datetime import datetime
from typing import Optional
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict


class ProductCreate(BaseModel):
    title: str
    category_id: int
    new_price: Decimal = Field(..., decimal_places=2)
    description: Optional[str] = None
    image: Optional[str] = None
    is_discount: bool = False
    is_available: bool = True
    is_new: bool = False
    is_popular: bool = False
    is_chef_recommended: bool = False
    old_price: Optional[Decimal] = Field(None, decimal_places=2)
    preparation_time: Optional[int] = None


class ProductUpdate(BaseModel):
    title: Optional[str] = None
    category_id: Optional[int] = None
    new_price: Optional[Decimal] = Field(None, decimal_places=2)
    description: Optional[str] = None
    image: Optional[str] = None
    is_discount: Optional[bool] = None
    is_available: Optional[bool] = None
    is_new: Optional[bool] = None
    is_popular: Optional[bool] = None
    is_chef_recommended: Optional[bool] = None
    old_price: Optional[Decimal] = Field(None, decimal_places=2)
    preparation_time: Optional[int] = None
    status: Optional[bool] = None


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    category_id: int
    title: str
    description: Optional[str] = None
    image: Optional[str] = None
    is_discount: bool
    is_available: bool
    is_new: bool
    is_popular: bool
    is_chef_recommended: bool
    new_price: Decimal
    old_price: Optional[Decimal] = None
    preparation_time: Optional[int] = None
    status: bool
    created_at: datetime
    updated_at: datetime