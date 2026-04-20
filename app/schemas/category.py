from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class CategoryCreate(BaseModel):
    title: str
    image: str


class CategoryUpdate(BaseModel):
    title: Optional[str] = None
    image: Optional[str] = None
    status: Optional[bool] = None


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    title: str
    image: str
    status: bool
    created_at: datetime
    updated_at: datetime
