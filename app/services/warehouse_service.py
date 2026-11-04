from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.warehouse import Warehouse
from app.models.inventory import Inventory
from app.models.user import User, UserRole
from app.schemas.warehouse import WarehouseCreate, WarehouseUpdate, WarehouseResponse

def get_all_warehouses(db: Session) -> List[dict]:
    warehouses = db.query(Warehouse).order_by(Warehouse.warehouse_id.asc()).all()
    res = []
    for wh in warehouses:
        # Count total inventory units stored in this warehouse
        stock_sum = db.query(Inventory).filter(Inventory.warehouse == wh.warehouse_name).all()
        total_units = sum(inv.current_stock for inv in stock_sum)
        unique_products = len(stock_sum)
        res.append({
            "warehouse_id": wh.warehouse_id,
            "warehouse_name": wh.warehouse_name,
            "location": wh.location,
            "capacity": wh.capacity,
            "contact_phone": wh.contact_phone,
            "is_active": wh.is_active,
            "created_at": wh.created_at,
            "total_units_stored": total_units,
            "unique_products_stored": unique_products,
            "utilization_percentage": round(min(100.0, (total_units / max(1, wh.capacity)) * 100), 1)
        })
    return res

def create_warehouse(db: Session, payload: WarehouseCreate, current_user: User) -> Warehouse:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Marketplace Administrators can register new warehouses."
        )

    existing = db.query(Warehouse).filter(Warehouse.warehouse_name == payload.warehouse_name.strip()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Warehouse '{payload.warehouse_name}' already exists."
        )

    wh = Warehouse(
        warehouse_name=payload.warehouse_name.strip(),
        location=payload.location.strip(),
        capacity=payload.capacity,
        contact_phone=payload.contact_phone,
        is_active=payload.is_active
    )
    db.add(wh)
    db.commit()
    db.refresh(wh)
    return wh

def update_warehouse(db: Session, warehouse_id: int, payload: WarehouseUpdate, current_user: User) -> Warehouse:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Marketplace Administrators can modify warehouse configurations."
        )

    wh = db.query(Warehouse).filter(Warehouse.warehouse_id == warehouse_id).first()
    if not wh:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Warehouse #{warehouse_id} not found."
        )

    old_name = wh.warehouse_name
    if payload.warehouse_name is not None and payload.warehouse_name.strip():
        new_name = payload.warehouse_name.strip()
        if new_name != old_name:
            dup = db.query(Warehouse).filter(Warehouse.warehouse_name == new_name).first()
            if dup:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Warehouse name '{new_name}' is already taken.")
            wh.warehouse_name = new_name
            # Also update references in inventory table
            db.query(Inventory).filter(Inventory.warehouse == old_name).update({"warehouse": new_name})

    if payload.location is not None:
        wh.location = payload.location.strip()
    if payload.capacity is not None:
        wh.capacity = payload.capacity
    if payload.contact_phone is not None:
        wh.contact_phone = payload.contact_phone
    if payload.is_active is not None:
        wh.is_active = payload.is_active

    db.commit()
    db.refresh(wh)
    return wh
