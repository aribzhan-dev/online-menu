from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CategoryCreate(BaseModel):
    title: str


class CategoryUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[bool] = None


class CategoryResponse(BaseModel):
    id: int
    company_id: int
    title: str
    status: bool
    created_at: datetime
    updated_at: datetime

    class ConfigDict:
        from_attributes = True