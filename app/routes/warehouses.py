from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.warehouse import WarehouseCreate, WarehouseUpdate, WarehouseResponse
from app.services import warehouse_service
from app.utils.security import get_current_active_user, require_admin
from app.models.user import User

router = APIRouter(prefix="/api/warehouses", tags=["Warehouses"])

@router.get("", response_model=List[dict])
def list_warehouses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """View all warehouses, capacities, and real-time inventory utilization."""
    return warehouse_service.get_all_warehouses(db)

@router.post("", response_model=WarehouseResponse, status_code=status.HTTP_201_CREATED)
def add_warehouse(
    payload: WarehouseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Add a new warehouse (Administrator privileges required)."""
    return warehouse_service.create_warehouse(db, payload, current_user)

@router.put("/{warehouse_id}", response_model=WarehouseResponse)
def update_warehouse(
    warehouse_id: int,
    payload: WarehouseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update warehouse details, capacity, and location."""
    return warehouse_service.update_warehouse(db, warehouse_id, payload, current_user)
