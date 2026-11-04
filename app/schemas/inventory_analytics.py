from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class InventoryAlertItem(BaseModel):
    product_id: int
    product_name: str
    vendor_id: int
    vendor_name: str
    current_stock: int
    reorder_level: int
    warehouse: str
    status: str
    indicator: str  # GREEN, YELLOW, RED
    notification: Optional[str] = None

class InventoryTurnoverItem(BaseModel):
    product_id: int
    product_name: str
    vendor_id: int
    vendor_name: str
    cogs: float
    average_inventory: float
    turnover_rate: float
    movement_classification: str  # Fast-Moving, Moderate-Moving, Slow-Moving

class InventoryTurnoverSummary(BaseModel):
    overall_turnover_rate: float
    total_cogs: float
    average_inventory_value: float
    fast_moving_products: List[InventoryTurnoverItem]
    slow_moving_products: List[InventoryTurnoverItem]
    vendor_performance: List[Dict[str, Any]]

class ForecastEvaluationMetrics(BaseModel):
    mae: float
    rmse: float
    mape: float
    accuracy_percentage: float
    trained_samples: int
    test_samples: int
    model_name: str = "Random Forest Regressor"

class ProductDemandForecast(BaseModel):
    product_id: int
    product_name: str
    category: str
    historical_sales_total: int
    predicted_demand_next_month: int
    actual_vs_predicted_variance: Optional[float] = None
    monthly_trend: List[Dict[str, Any]] = []

class ForecastingResponse(BaseModel):
    forecasts: List[ProductDemandForecast]
    evaluation: ForecastEvaluationMetrics

class ReplenishmentItem(BaseModel):
    product_id: int
    product_name: str
    current_stock: int
    reorder_level: int
    forecast_demand: int
    target_stock_level: int
    recommended_reorder_qty: int
    preferred_vendor_id: int
    preferred_vendor_name: str
    urgency: str  # CRITICAL, HIGH, MEDIUM, LOW
