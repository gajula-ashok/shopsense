from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.vendor import Vendor
from app.models.stock_movement import StockMovement, MovementType
from app.models.transaction import Transaction
from app.models.user import User, UserRole
from app.schemas.inventory_analytics import (
    InventoryAlertItem,
    InventoryTurnoverSummary,
    InventoryTurnoverItem,
    ReplenishmentItem
)

def get_low_stock_alerts(db: Session, current_user: User) -> List[InventoryAlertItem]:
    """Identify products where current_stock <= reorder_level with GREEN / YELLOW / RED status indicators."""
    query = db.query(Inventory).join(Product).join(Vendor, Product.vendor_id == Vendor.vendor_id)

    if current_user.role == UserRole.VENDOR and current_user.vendor:
        query = query.filter(Product.vendor_id == current_user.vendor.vendor_id)

    items = query.all()
    alerts = []
    for inv in items:
        p = inv.product
        v = p.vendor if p else None
        stock = inv.current_stock
        reorder = inv.reorder_level

        if stock == 0:
            indicator = "RED"
            status_text = "OUT OF STOCK"
            notif = f"URGENT: '{p.product_name}' is completely out of stock! Immediate restock needed."
        elif stock <= reorder:
            indicator = "YELLOW"
            status_text = "LOW STOCK"
            notif = f"WARNING: '{p.product_name}' stock ({stock}) has fallen to or below reorder threshold ({reorder})."
        else:
            indicator = "GREEN"
            status_text = "AVAILABLE"
            notif = None

        alerts.append(InventoryAlertItem(
            product_id=p.product_id,
            product_name=p.product_name,
            vendor_id=p.vendor_id,
            vendor_name=v.business_name if v else "Unknown Vendor",
            current_stock=stock,
            reorder_level=reorder,
            warehouse=inv.warehouse or "Main Warehouse",
            status=status_text,
            indicator=indicator,
            notification=notif
        ))

    # Return items sorted by criticality: RED first, then YELLOW, then GREEN
    order_map = {"RED": 0, "YELLOW": 1, "GREEN": 2}
    alerts.sort(key=lambda x: order_map[x.indicator])
    return alerts

def record_stock_movement(
    db: Session,
    product_id: int,
    quantity: int,
    movement_type: str = "ADJUSTMENT",
    reference: Optional[str] = None,
    warehouse: Optional[str] = None
) -> StockMovement:
    """Record physical inventory movement (addition or reduction) and adjust stock."""
    inv = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if inv:
        if warehouse:
            inv.warehouse = warehouse
        # Adjust stock safely
        inv.current_stock = max(0, inv.current_stock + quantity)
        p = db.query(Product).filter(Product.product_id == product_id).first()
        if p:
            p.stock = inv.current_stock
        db.commit()

    movement = StockMovement(
        product_id=product_id,
        quantity=quantity,
        movement_type=movement_type,
        reference=reference,
        warehouse=warehouse or (inv.warehouse if inv else "Main Warehouse")
    )
    db.add(movement)
    db.commit()
    db.refresh(movement)
    return movement

def get_stock_movements(
    db: Session,
    product_id: Optional[int] = None,
    current_user: Optional[User] = None
) -> List[Dict[str, Any]]:
    query = db.query(StockMovement).join(Product)
    if product_id:
        query = query.filter(StockMovement.product_id == product_id)
    if current_user and current_user.role == UserRole.VENDOR and current_user.vendor:
        query = query.filter(Product.vendor_id == current_user.vendor.vendor_id)

    movements = query.order_by(StockMovement.movement_id.desc()).limit(100).all()
    return [
        {
            "movement_id": m.movement_id,
            "product_id": m.product_id,
            "product_name": m.product.product_name if m.product else "N/A",
            "quantity": m.quantity,
            "movement_type": m.movement_type,
            "reference": m.reference,
            "warehouse": m.warehouse,
            "created_at": m.created_at
        }
        for m in movements
    ]

def calculate_inventory_turnover(db: Session, current_user: User) -> InventoryTurnoverSummary:
    """
    Inventory Turnover = Cost of Goods Sold / Average Inventory
    COGS approximated as sum(amount) from transactions (or price * quantity).
    Average inventory approximated as (current_stock + initial_or_sold_stock) / 2 * unit_cost.
    """
    products_q = db.query(Product).join(Inventory).join(Vendor)
    if current_user.role == UserRole.VENDOR and current_user.vendor:
        products_q = products_q.filter(Product.vendor_id == current_user.vendor.vendor_id)
    products = products_q.all()

    turnover_items = []
    total_cogs = 0.0
    total_avg_inv_val = 0.0

    vendor_perf_map = {}

    for p in products:
        unit_price = float(p.price)
        # Sales metrics from transactions
        sales_q = db.query(
            func.coalesce(func.sum(Transaction.quantity), 0),
            func.coalesce(func.sum(Transaction.amount), 0.0)
        ).filter(Transaction.product_id == p.product_id).first()

        qty_sold = int(sales_q[0]) if sales_q else 0
        revenue = float(sales_q[1]) if sales_q else 0.0

        # Cost of goods sold (COGS)
        cogs = round(qty_sold * unit_price, 2)
        total_cogs += cogs

        # Average Inventory = (Current Stock + Ending Stock) / 2 * Cost
        current_stk = p.inventory.current_stock if p.inventory else p.stock
        avg_units = max(1.0, (current_stk + (current_stk + qty_sold)) / 2.0)
        avg_inv_value = round(avg_units * unit_price, 2)
        total_avg_inv_val += avg_inv_value

        turnover_rate = round(cogs / avg_inv_value, 2) if avg_inv_value > 0 else 0.0

        if turnover_rate >= 1.5:
            classification = "Fast-Moving"
        elif turnover_rate >= 0.5:
            classification = "Moderate-Moving"
        else:
            classification = "Slow-Moving"

        v_name = p.vendor.business_name if p.vendor else "Unknown"
        item = InventoryTurnoverItem(
            product_id=p.product_id,
            product_name=p.product_name,
            vendor_id=p.vendor_id,
            vendor_name=v_name,
            cogs=cogs,
            average_inventory=avg_inv_value,
            turnover_rate=turnover_rate,
            movement_classification=classification
        )
        turnover_items.append(item)

        # Track per vendor
        if v_name not in vendor_perf_map:
            vendor_perf_map[v_name] = {"cogs": 0.0, "avg_inv": 0.0, "items_count": 0}
        vendor_perf_map[v_name]["cogs"] += cogs
        vendor_perf_map[v_name]["avg_inv"] += avg_inv_value
        vendor_perf_map[v_name]["items_count"] += 1

    overall_turnover = round(total_cogs / total_avg_inv_val, 2) if total_avg_inv_val > 0 else 0.0

    # Sort fast and slow moving
    sorted_items = sorted(turnover_items, key=lambda x: x.turnover_rate, reverse=True)
    fast_moving = [x for x in sorted_items if x.movement_classification == "Fast-Moving"]
    slow_moving = [x for x in sorted_items if x.movement_classification == "Slow-Moving"]

    vendor_perf_list = []
    for v_name, stats in vendor_perf_map.items():
        v_turnover = round(stats["cogs"] / stats["avg_inv"], 2) if stats["avg_inv"] > 0 else 0.0
        vendor_perf_list.append({
            "vendor_name": v_name,
            "turnover_rate": v_turnover,
            "total_cogs": round(stats["cogs"], 2),
            "average_inventory": round(stats["avg_inv"], 2),
            "total_products": stats["items_count"]
        })

    return InventoryTurnoverSummary(
        overall_turnover_rate=overall_turnover,
        total_cogs=round(total_cogs, 2),
        average_inventory_value=round(total_avg_inv_val, 2),
        fast_moving_products=fast_moving[:10],
        slow_moving_products=slow_moving[:10],
        vendor_performance=vendor_perf_list
    )
