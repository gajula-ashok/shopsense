from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.analytics import (
    MarketplaceSummary,
    VendorPerformanceItem,
    ProductPerformanceItem,
    RevenueTrendItem,
    CategoryPerformanceItem,
)
from app.schemas.customer_recommendation import (
    CustomerBehaviorSummary,
    CustomerSegmentationResponse
)
from app.services import analytics_service
from app.customer import analytics as customer_analytics
from app.customer import segmentation as customer_segmentation
from app.utils.security import get_current_active_user, require_admin
from app.models.user import User

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/summary", response_model=MarketplaceSummary)
def get_analytics_summary(
    vendor_id: Optional[int] = Query(None, description="Optional vendor filter for Admin"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get high-level summary KPIs (Total Revenue, Transactions, Quantity Sold, ATV)."""
    return analytics_service.get_summary(db, current_user, vendor_id)

@router.get("/vendor-performance", response_model=List[VendorPerformanceItem])
def get_vendor_performance_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get vendor performance metrics with revenue, transaction counts, and quantity sold."""
    return analytics_service.get_vendor_performance(db, current_user)

@router.get("/product-performance", response_model=List[ProductPerformanceItem])
def get_product_performance_metrics(
    vendor_id: Optional[int] = Query(None, description="Optional vendor filter for Admin"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get product performance analytics including units sold, revenue, and stock status."""
    return analytics_service.get_product_performance(db, current_user, vendor_id)

@router.get("/revenue-trend", response_model=List[RevenueTrendItem])
def get_revenue_trend_metrics(
    vendor_id: Optional[int] = Query(None, description="Optional vendor filter for Admin"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get time-series revenue and sales trends aggregated by date."""
    return analytics_service.get_revenue_trend(db, current_user, vendor_id)

@router.get("/category-performance", response_model=List[CategoryPerformanceItem])
def get_category_performance_metrics(
    vendor_id: Optional[int] = Query(None, description="Optional vendor filter for Admin"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get revenue and unit sales breakdown grouped by product category."""
    return analytics_service.get_category_performance(db, current_user, vendor_id)

# ===================================================
# Milestone 2: Customer Analytics & Segmentation APIs
# ===================================================
@router.get("/customers", response_model=List[CustomerBehaviorSummary])
def get_customers_behavior(
    customer_id: Optional[int] = Query(None, description="Filter for single customer"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Analyze customer behavior: total orders, total spent, AOV, purchase frequency, top products."""
    return customer_analytics.get_customer_behavior_metrics(db, customer_id)

@router.get("/customer-behavior", response_model=List[CustomerBehaviorSummary])
def get_customer_behavior_alias(
    customer_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Alias for /api/analytics/customers behavior analysis."""
    return customer_analytics.get_customer_behavior_metrics(db, customer_id)

@router.get("/segments", response_model=CustomerSegmentationResponse)
def get_customer_segments(
    n_clusters: int = Query(3, ge=2, le=6),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Customer segmentation using K-Means with StandardScaler and Silhouette Score evaluation."""
    return customer_segmentation.perform_customer_segmentation(db, n_clusters)
