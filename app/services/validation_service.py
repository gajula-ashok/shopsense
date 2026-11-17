from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import SessionLocal
from app.models.analytics_metadata import DashboardValidationLog
from app.models.transaction import Transaction
from app.models.product import Product
from app.models.user import User, UserRole
from app.models.vendor import Vendor
from app.models.inventory import Inventory
from app.services.revenue_service import calculate_advanced_revenue

def validate_dashboard_data_consistency() -> Dict[str, Any]:
    """
    Automated Dashboard Data Consistency Validation:
    Compares database entity counts & values with dashboard analytical outputs:
    1. Database Revenue vs Dashboard Revenue
    2. Database Product Count vs Dashboard Product Count
    3. Database Customer Count vs Dashboard Customer Count
    4. Database Vendor Count vs Dashboard Vendor Count
    5. Database Inventory Units vs Dashboard Inventory Units
    6. Database Order Count vs Dashboard Order Count
    Target: Dashboard Data Consistency >= 99%
    """
    db: Session = SessionLocal()
    admin = db.query(User).filter(User.role == UserRole.ADMIN).first()

    # 1. DB ground truth queries
    db_rev = float(db.query(func.coalesce(func.sum(Transaction.amount), 0.0)).scalar())
    db_prods = int(db.query(Product).count())
    db_custs = int(db.query(User).filter(User.role == UserRole.CUSTOMER).count())
    db_vends = int(db.query(Vendor).count())
    db_inv_units = int(db.query(func.coalesce(func.sum(Inventory.current_stock), 0)).scalar())
    db_orders = int(db.query(Transaction).count())

    # 2. Analytical service outputs
    dash_analytics = calculate_advanced_revenue(db, admin)
    dash_rev = float(dash_analytics["total_revenue"])
    dash_orders = int(dash_analytics["total_orders"])

    from app.services.analytics_service import get_summary
    dash_sum = get_summary(db, admin)
    dash_prods = int(dash_sum["total_products"])
    dash_vends = int(dash_sum["total_vendors"])

    from app.inventory.inventory_tracking import get_low_stock_alerts
    dash_alerts = get_low_stock_alerts(db, admin)
    dash_inv_units = sum(a.current_stock for a in dash_alerts)

    from app.customer.analytics import get_customer_behavior_metrics
    dash_custs = len(get_customer_behavior_metrics(db))

    # Comparisons
    comparisons = [
        {
            "metric": "Marketplace Revenue",
            "db_value": round(db_rev, 2),
            "dashboard_value": round(dash_rev, 2),
            "match": abs(db_rev - dash_rev) < 0.01,
            "diff": round(abs(db_rev - dash_rev), 2)
        },
        {
            "metric": "Product Count",
            "db_value": db_prods,
            "dashboard_value": dash_prods,
            "match": db_prods == dash_prods,
            "diff": abs(db_prods - dash_prods)
        },
        {
            "metric": "Customer Count",
            "db_value": db_custs,
            "dashboard_value": dash_custs,
            "match": db_custs == dash_custs,
            "diff": abs(db_custs - dash_custs)
        },
        {
            "metric": "Vendor Count",
            "db_value": db_vends,
            "dashboard_value": dash_vends,
            "match": db_vends == dash_vends,
            "diff": abs(db_vends - dash_vends)
        },
        {
            "metric": "Inventory Stock Units",
            "db_value": db_inv_units,
            "dashboard_value": dash_inv_units,
            "match": db_inv_units == dash_inv_units,
            "diff": abs(db_inv_units - dash_inv_units)
        },
        {
            "metric": "Total Transactions / Orders",
            "db_value": db_orders,
            "dashboard_value": dash_orders,
            "match": db_orders == dash_orders,
            "diff": abs(db_orders - dash_orders)
        }
    ]

    matched_count = sum(1 for c in comparisons if c["match"])
    total_metrics = len(comparisons)
    consistency_pct = round((matched_count / total_metrics) * 100.0, 2)
    mismatches = [c for c in comparisons if not c["match"]]

    status = "PASS" if consistency_pct >= 99.0 else "FAIL"

    # Save validation log to database
    try:
        log = DashboardValidationLog(
            validation_time=datetime.now(),
            consistency_percentage=consistency_pct,
            status=status,
            comparisons=comparisons,
            mismatches=mismatches,
            notes=f"Validated {matched_count}/{total_metrics} core entities against PostgreSQL ground truth."
        )
        db.add(log)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error persisting validation log: {e}")
    finally:
        db.close()

    return {
        "timestamp": datetime.now().isoformat(),
        "consistency_percentage": consistency_pct,
        "target_met": (consistency_pct >= 99.0),
        "status": status,
        "comparisons": comparisons,
        "mismatches": mismatches
    }

def get_latest_validation_history(limit: int = 10) -> List[Dict[str, Any]]:
    db = SessionLocal()
    try:
        rows = db.query(DashboardValidationLog).order_by(DashboardValidationLog.validation_time.desc()).limit(limit).all()
        return [{
            "id": r.id,
            "validation_time": r.validation_time.strftime("%Y-%m-%d %H:%M:%S") if r.validation_time else "N/A",
            "consistency_percentage": r.consistency_percentage,
            "status": r.status,
            "comparisons": r.comparisons,
            "mismatches": r.mismatches,
            "notes": r.notes
        } for r in rows]
    finally:
        db.close()
