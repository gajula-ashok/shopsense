from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.inventory import InventoryUpdate, InventoryResponse
from app.schemas.inventory_analytics import (
    InventoryAlertItem,
    InventoryTurnoverSummary,
    ForecastingResponse,
    ReplenishmentItem
)
from app.schemas.stock_movement import StockMovementCreate, StockMovementResponse
from app.services import inventory_service
from app.inventory import inventory_tracking, inventory_forecasting, replenishment
from app.utils.security import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/api/inventory", tags=["Inventory"])

# 1. Milestone 1 Core Inventory Endpoints
@router.get("", response_model=List[InventoryResponse])
def get_inventory(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (IN STOCK, LOW STOCK, OUT OF STOCK)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """View inventory levels and warehouse status with visual status categorization."""
    return inventory_service.get_inventory_items(db, current_user, status_filter)

@router.get("/alerts", response_model=List[InventoryAlertItem])
def get_inventory_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Automatic low stock alerts with GREEN / YELLOW / RED status indicators."""
    return inventory_tracking.get_low_stock_alerts(db, current_user)

@router.get("/turnover", response_model=InventoryTurnoverSummary)
def get_inventory_turnover(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Calculate Inventory Turnover = COGS / Average Inventory, fast and slow moving items."""
    return inventory_tracking.calculate_inventory_turnover(db, current_user)

@router.get("/forecast", response_model=ForecastingResponse)
def get_demand_forecast(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Machine learning demand forecasting via Random Forest Regressor with MAE, RMSE, MAPE metrics."""
    return inventory_forecasting.train_and_forecast_demand(db, current_user)

@router.get("/replenishment", response_model=List[ReplenishmentItem])
def get_replenishment_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Calculated recommended replenishment quantities based on current stock, reorder level, and ML forecast."""
    return replenishment.calculate_replenishment_recommendations(db, current_user)

@router.get("/movements", response_model=List[dict])
def list_stock_movements(
    product_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """View inventory movements ledger (additions, reductions, adjustments)."""
    return inventory_tracking.get_stock_movements(db, product_id, current_user)

@router.post("/movements", response_model=dict, status_code=status.HTTP_201_CREATED)
def record_movement(
    payload: StockMovementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Record physical stock adjustment (stock in/out) and update live inventory."""
    mov = inventory_tracking.record_stock_movement(
        db,
        product_id=payload.product_id,
        quantity=payload.quantity,
        movement_type=payload.movement_type,
        reference=payload.reference,
        warehouse=payload.warehouse
    )
    return {
        "movement_id": mov.movement_id,
        "product_id": mov.product_id,
        "quantity": mov.quantity,
        "movement_type": mov.movement_type,
        "reference": mov.reference,
        "warehouse": mov.warehouse,
        "created_at": mov.created_at
    }

@router.get("/{product_id}", response_model=InventoryResponse)
def get_inventory_for_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retrieve detailed inventory tracking for a single product."""
    return inventory_service.get_inventory_by_product_id(db, product_id, current_user)

@router.put("/{product_id}", response_model=InventoryResponse)
def update_inventory(
    product_id: int,
    payload: InventoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update stock counts, reorder levels, or warehouse location."""
    return inventory_service.update_inventory_by_product_id(db, product_id, payload, current_user)
