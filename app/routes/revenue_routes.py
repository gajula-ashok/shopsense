from fastapi import APIRouter, Depends, Query, HTTPException, Response, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.database import get_db
from app.models.user import User, UserRole
from app.utils.security import get_current_active_user, require_admin
from app.services import (
    revenue_service,
    workflow_service,
    mlflow_service,
    report_service,
    validation_service,
    performance_service,
    analytics_service
)
from app.customer import analytics as customer_analytics
from app.customer import segmentation as customer_segmentation
from app.inventory import inventory_forecasting
from app.recommendation.recommendation import recommend_products

router = APIRouter(prefix="/analytics", tags=["Milestone 3 Analytics & Reporting"])

# ==========================================
# 1. Revenue Analytics
# ==========================================
@router.get("/revenue", summary="Get comprehensive revenue metrics and GMV")
def get_revenue_analytics(
    vendor_id: Optional[int] = Query(None, description="Optional vendor ID filter"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retrieve GMV, total revenue, average order value, total orders, and growth rates."""
    return revenue_service.calculate_advanced_revenue(db, current_user, vendor_id=vendor_id)

@router.get("/revenue/monthly", summary="Get monthly revenue trend breakdown")
def get_monthly_revenue(
    vendor_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Monthly revenue aggregation with order counts and units sold."""
    rev = revenue_service.calculate_advanced_revenue(db, current_user, vendor_id=vendor_id)
    return rev.get("monthly_revenue", [])

@router.get("/revenue/growth", summary="Get latest revenue growth percentage")
def get_revenue_growth(
    vendor_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Month-over-month revenue growth rate percentage."""
    rev = revenue_service.calculate_advanced_revenue(db, current_user, vendor_id=vendor_id)
    return {
        "growth_rate_pct": rev.get("growth_rate_pct", 0.0),
        "total_revenue": rev.get("total_revenue", 0.0),
        "gmv": rev.get("gmv", 0.0)
    }

# ==========================================
# 2. Forecasting
# ==========================================
@router.get("/forecast", summary="Get demand forecasts for all inventory items")
def get_inventory_forecasts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Trained Random Forest demand forecasts with accuracy, MAE, and RMSE metrics."""
    return inventory_forecasting.train_and_forecast_demand(db, current_user)

@router.get("/forecast/{product_id}", summary="Get demand forecast for a single product")
def get_single_product_forecast(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Demand forecast and 30-day projection for a specific product ID."""
    fc = inventory_forecasting.train_and_forecast_demand(db, current_user)
    match = next((f for f in fc.forecasts if f.product_id == product_id), None)
    if not match:
        raise HTTPException(status_code=404, detail=f"No forecast found for product #{product_id}")
    return {
        "product_id": match.product_id,
        "product_name": match.product_name,
        "category": match.category,
        "predicted_demand_next_month": match.predicted_demand_next_month,
        "historical_sales_total": match.historical_sales_total,
        "accuracy_percentage": fc.evaluation.accuracy_percentage,
        "evaluation_rmse": fc.evaluation.rmse
    }

# ==========================================
# 3. Customer Analytics
# ==========================================
@router.get("/customers", summary="List customer profiles and order histories")
def list_customer_analytics(
    customer_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Comprehensive customer behavior analysis with spend, orders, and preferred categories."""
    return customer_analytics.get_customer_behavior_metrics(db, customer_id)

@router.get("/customer-segments", summary="Get K-Means customer segmentation clusters")
def get_customer_segments_clusters(
    n_clusters: Optional[int] = Query(None, ge=2, le=6),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Segment customers using RFM analysis, StandardScaler, and optimal Silhouette scoring."""
    return customer_segmentation.perform_customer_segmentation(db, n_clusters)

@router.get("/customer-metrics", summary="High-level customer behavioral summary metrics")
def get_customer_aggregate_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Aggregate customer metrics: count, active shoppers, average lifetime value."""
    custs = customer_analytics.get_customer_behavior_metrics(db)
    total_spent = sum(c.total_spent for c in custs)
    total_orders = sum(c.total_orders for c in custs)
    return {
        "total_customers": len(custs),
        "total_orders": total_orders,
        "total_spend": round(total_spent, 2),
        "average_customer_ltv": round(total_spent / max(1, len(custs)), 2),
        "average_orders_per_customer": round(total_orders / max(1, len(custs)), 1)
    }

# ==========================================
# 4. Recommendations
# ==========================================
@router.get("/recommendations/{customer_id}", summary="Get personalized recommendations for customer")
def get_customer_recommendations_endpoint(
    customer_id: int,
    top_n: int = Query(5, ge=1, le=15),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Collaborative filtering recommendations with cosine similarity matching."""
    if current_user.role == UserRole.CUSTOMER and current_user.user_id != customer_id:
        customer_id = current_user.user_id
    return recommend_products(db, customer_id=customer_id, top_n=top_n)

# ==========================================
# 5. Vendor Analytics
# ==========================================
@router.get("/vendor-performance", summary="Vendor ranking and performance benchmarking")
def get_vendor_performance_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Ranked vendor list with sales volume, revenue shares, and fulfillment metrics."""
    return analytics_service.get_vendor_performance(db, current_user)

@router.get("/vendor/{vendor_id}/sales", summary="Vendor-specific sales and order breakdown")
def get_single_vendor_sales(
    vendor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Detailed revenue and product sales analysis for a specific vendor."""
    rev = revenue_service.calculate_advanced_revenue(db, current_user, vendor_id=vendor_id)
    return {
        "vendor_id": vendor_id,
        "total_revenue": rev["total_revenue"],
        "total_orders": rev["total_orders"],
        "total_units_sold": rev["total_units_sold"],
        "monthly_breakdown": rev["monthly_revenue"],
        "top_products": rev["top_products"]
    }

# ==========================================
# 6. MLflow Model Registry Endpoints
# ==========================================
@router.get("/models", summary="List registered models in MLflow registry")
def list_mlflow_models(current_user: User = Depends(require_admin)):
    """View registered models, current production versions, and tracking metrics."""
    return mlflow_service.get_registered_models()

@router.get("/models/{model_name}/history", summary="Get model version history")
def get_mlflow_model_history(model_name: str, current_user: User = Depends(require_admin)):
    """Retrieve full version and evaluation history for a given model."""
    return mlflow_service.get_model_history(model_name)

# ==========================================
# 7. Workflow Pipeline Endpoints
# ==========================================
@router.post("/workflows/run", summary="Trigger manual workflow pipeline execution")
def trigger_workflow_execution(current_user: User = Depends(require_admin)):
    """Execute all scheduled tasks (inventory, revenue, ML training, cache refresh)."""
    return workflow_service.run_all_workflows()

@router.get("/workflows/history", summary="Get workflow execution audit logs")
def get_workflow_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_admin)
):
    """List execution history and status records for scheduled analytics tasks."""
    return workflow_service.get_workflow_history(limit)

@router.get("/workflows/stats", summary="Get workflow success rate and statistics")
def get_workflow_stats(current_user: User = Depends(require_admin)):
    """Calculates Workflow Success Rate = (Successful / Total) * 100 with target = 100%."""
    return workflow_service.get_workflow_statistics()

# ==========================================
# 8. Report Export Endpoints (PDF & Excel)
# ==========================================
@router.get("/reports/excel", summary="Download comprehensive multi-sheet Excel report")
def download_excel_report(
    vendor_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_active_user)
):
    """Generates an OpenPyXL workbook containing 10 structured analytics sheets."""
    # Enforce vendor data isolation: Vendors can ONLY access their own vendor_id
    effective_vendor_id = vendor_id
    if current_user.role == UserRole.VENDOR:
        effective_vendor_id = current_user.vendor.vendor_id if current_user.vendor else -1
    buffer = report_service.generate_excel_report(vendor_id=effective_vendor_id)
    return Response(
        content=buffer.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=ShopSense_Marketplace_Analytics.xlsx"}
    )

@router.get("/reports/pdf", summary="Download executive summary PDF report")
def download_pdf_report(
    vendor_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_active_user)
):
    """Generates a ReportLab executive summary PDF report."""
    # Enforce vendor data isolation: Vendors can ONLY access their own vendor_id
    effective_vendor_id = vendor_id
    if current_user.role == UserRole.VENDOR:
        effective_vendor_id = current_user.vendor.vendor_id if current_user.vendor else -1
    buffer = report_service.generate_pdf_report(vendor_id=effective_vendor_id)
    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=ShopSense_Marketplace_Report.pdf"}
    )

# ==========================================
# 9. Dashboard Data Consistency Validation
# ==========================================
@router.post("/validation/run", summary="Run dashboard data consistency validation")
def run_dashboard_validation(current_user: User = Depends(require_admin)):
    """Validates DB vs Dashboard values across 6 core entities with target >= 99%."""
    return validation_service.validate_dashboard_data_consistency()

@router.get("/validation/history", summary="Get validation history logs")
def get_validation_history(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(require_admin)
):
    """Retrieve history of consistency validation runs and any recorded mismatches."""
    return validation_service.get_latest_validation_history(limit)

# ==========================================
# 10. Performance Testing Benchmarks
# ==========================================
@router.post("/performance/run", summary="Run API latency and throughput benchmarks")
def run_api_performance_benchmarks(
    iterations: int = Query(5, ge=1, le=20),
    current_user: User = Depends(require_admin)
):
    """Benchmark core APIs against target <= 300 ms response time."""
    return performance_service.run_performance_benchmarks(iterations=iterations)

@router.get("/performance/history", summary="Get performance benchmark history")
def get_api_performance_history(
    limit: int = Query(25, ge=1, le=100),
    current_user: User = Depends(require_admin)
):
    """History of latency and RPS performance runs."""
    return performance_service.get_performance_history(limit)
