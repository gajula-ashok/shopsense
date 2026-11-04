from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class StockMovementCreate(BaseModel):
    product_id: int
    quantity: int
    movement_type: str = "ADJUSTMENT"
    reference: Optional[str] = None
    warehouse: Optional[str] = None

class StockMovementResponse(BaseModel):
    movement_id: int
    product_id: int
    product_name: Optional[str] = None
    quantity: int
    movement_type: str
    reference: Optional[str] = None
    warehouse: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
