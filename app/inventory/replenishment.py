from typing import List
from sqlalchemy.orm import Session
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.vendor import Vendor
from app.models.user import User, UserRole
from app.schemas.inventory_analytics import ReplenishmentItem
from app.inventory.inventory_forecasting import train_and_forecast_demand

def calculate_replenishment_recommendations(db: Session, current_user: User) -> List[ReplenishmentItem]:
    """
    Replenishment Recommendation Engine
    Formula:
        Target Stock Level = max(Reorder Level * 2, Forecast Demand + Safety Stock)
        Recommended Reorder Quantity = max(0, Target Stock Level - Current Stock)
    Considers current stock, reorder level, forecast demand, and vendor availability.
    """
    # 1. Fetch ML demand forecasts
    forecasting_result = train_and_forecast_demand(db, current_user)
    forecast_map = {f.product_id: f.predicted_demand_next_month for f in forecasting_result.forecasts}

    query = db.query(Inventory).join(Product).join(Vendor, Product.vendor_id == Vendor.vendor_id)
    if current_user.role == UserRole.VENDOR and current_user.vendor:
        query = query.filter(Product.vendor_id == current_user.vendor.vendor_id)

    inventory_items = query.all()
    recommendations = []

    for inv in inventory_items:
        p = inv.product
        v = p.vendor if p else None
        current_stock = inv.current_stock
        reorder_level = inv.reorder_level

        # Predicted demand for next 30 days
        forecast_demand = forecast_map.get(p.product_id, max(5, reorder_level))

        # Target Stock Level includes buffer/safety stock
        safety_stock = int(round(reorder_level * 0.5))
        target_stock_level = int(forecast_demand + safety_stock + reorder_level)

        # Recommended quantity = Target - Current
        reorder_qty = max(0, target_stock_level - current_stock)

        # Determine Urgency
        if current_stock == 0:
            urgency = "CRITICAL"
        elif current_stock <= reorder_level:
            urgency = "HIGH"
        elif current_stock < target_stock_level * 0.7:
            urgency = "MEDIUM"
        else:
            urgency = "LOW"

        # Even if urgency is LOW, provide replenishment recommendation if reorder_qty > 0
        recommendations.append(ReplenishmentItem(
            product_id=p.product_id,
            product_name=p.product_name,
            current_stock=current_stock,
            reorder_level=reorder_level,
            forecast_demand=forecast_demand,
            target_stock_level=target_stock_level,
            recommended_reorder_qty=reorder_qty,
            preferred_vendor_id=p.vendor_id,
            preferred_vendor_name=v.business_name if v else "Primary Vendor",
            urgency=urgency
        ))

    urgency_priority = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    recommendations.sort(key=lambda x: (urgency_priority[x.urgency], -x.recommended_reorder_qty))
    return recommendations
