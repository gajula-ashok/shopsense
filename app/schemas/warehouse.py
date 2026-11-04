from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class WarehouseBase(BaseModel):
    warehouse_name: str = Field(..., min_length=2, max_length=120)
    location: str = Field(..., min_length=2, max_length=200)
    capacity: int = Field(10000, ge=1)
    contact_phone: Optional[str] = None
    is_active: bool = True

class WarehouseCreate(WarehouseBase):
    pass

class WarehouseUpdate(BaseModel):
    warehouse_name: Optional[str] = Field(None, min_length=2, max_length=120)
    location: Optional[str] = Field(None, min_length=2, max_length=200)
    capacity: Optional[int] = Field(None, ge=1)
    contact_phone: Optional[str] = None
    is_active: Optional[bool] = None

class WarehouseResponse(WarehouseBase):
    warehouse_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
