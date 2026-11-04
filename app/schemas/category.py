from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CategoryBase(BaseModel):
    category_name: str = Field(..., min_length=2, max_length=100)
    parent_id: Optional[int] = None
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    category_name: Optional[str] = Field(None, min_length=2, max_length=100)
    parent_id: Optional[int] = None
    description: Optional[str] = None

class CategoryResponse(CategoryBase):
    category_id: int
    created_at: datetime
    parent_name: Optional[str] = None

    model_config = {"from_attributes": True}

class CategoryTreeResponse(BaseModel):
    category_id: int
    category_name: str
    description: Optional[str] = None
    subcategories: List["CategoryTreeResponse"] = []

    model_config = {"from_attributes": True}
