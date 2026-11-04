"""
Full ML Audit - runs all 4 Milestone 2 ML modules against real DB
and prints actual measured metrics.
"""
import sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "C:/Users/chiru/OneDrive/Desktop/ShopSense")

from app.database import SessionLocal
from app.models.user import User, UserRole

db = SessionLocal()

print("=" * 65)
print("  SHOPSENSE MILESTONE 2 - ML AUDIT (ACTUAL DB RESULTS)")
print("=" * 65)

# --- 1. INVENTORY FORECASTING ---
print("\n[1] INVENTORY FORECASTING")
try:
    admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
    from app.inventory.inventory_forecasting import train_and_forecast_demand
    fc = train_and_forecast_demand(db, admin)
    ev = fc.evaluation
    print(f"    Model         : {ev.model_name}")
    print(f"    Train samples : {ev.trained_samples}")
    print(f"    Test samples  : {ev.test_samples}")
    print(f"    MAE           : {ev.mae}")
    print(f"    RMSE          : {ev.rmse}")
    print(f"    MAPE          : {ev.mape}%")
    print(f"    Accuracy (NRMSE-based): {ev.accuracy_percentage}%")
    print(f"    Forecasts generated  : {len(fc.forecasts)}")
    print(f"    Status: {'PASS (>=80%)' if ev.accuracy_percentage >= 80 else 'NEEDS WORK'}")
except Exception as e:
    print(f"    ERROR: {e}")
    import traceback; traceback.print_exc()

# --- 2. CUSTOMER SEGMENTATION ---
print("\n[2] CUSTOMER SEGMENTATION")
try:
    from app.customer.segmentation import perform_customer_segmentation
    res = perform_customer_segmentation(db)
    print(f"    Optimal k     : {res.optimal_clusters}")
    print(f"    Silhouette    : {res.silhouette_score:.4f}")
    print(f"    Target        : {res.evaluation_target}")
    print(f"    Target met    : {res.target_met}")
    print(f"    Segments:")
    for s in res.segment_summary:
        print(f"      - {s.segment_name:25s} | Count={s.count:3d} ({s.percentage}%) | Avg Spend=${s.avg_spent:,.2f} | Avg Orders={s.avg_orders}")
    print(f"    Status: {'PASS (>=0.35)' if res.silhouette_score >= 0.35 else 'BELOW 0.35'}")
except Exception as e:
    print(f"    ERROR: {e}")
    import traceback; traceback.print_exc()

# --- 3. RECOMMENDATION ENGINE ---
print("\n[3] RECOMMENDATION ENGINE")
try:
    from app.recommendation.recommendation import evaluate_recommendations, recommend_products
    ev = evaluate_recommendations(db, k=5)
    print(f"    Precision@5   : {ev.precision_at_k:.4f} ({ev.precision_at_k*100:.2f}%)")
    print(f"    Target        : {ev.precision_target}")
    print(f"    Customers eval: {ev.total_customers_evaluated}")
    print(f"    Method        : {ev.evaluation_method}")
    print(f"    Target met    : {ev.target_met}")

    # Sample customer recommendations and check for uniqueness
    from app.models.interaction import ProductInteraction
    sample_cid = db.query(ProductInteraction.user_id).first()
    if sample_cid:
        recs = recommend_products(db, customer_id=sample_cid[0], top_n=5)
        p_names = [r.product_name for r in recs.recommendations]
        print(f"    Sample recs for customer {sample_cid[0]}:")
        for idx, r in enumerate(recs.recommendations, 1):
            print(f"      {idx}. [ID {r.product_id}] {r.product_name[:38]:38s} | Cat={r.category} | ${r.price}")
        p_ids = [r.product_id for r in recs.recommendations]
        has_dups = len(p_ids) != len(set(p_ids))
        print(f"    Duplicate Check: {'FAIL (duplicates found)' if has_dups else 'PASS (all unique items)'}")
except Exception as e:
    print(f"    ERROR: {e}")
    import traceback; traceback.print_exc()

# --- 4. INVENTORY MODULE ---
print("\n[4] INVENTORY MODULE")
try:
    admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
    from app.inventory.inventory_tracking import get_low_stock_alerts, get_stock_movements, calculate_inventory_turnover
    from app.inventory.replenishment import calculate_replenishment_recommendations
    from app.services.warehouse_service import get_all_warehouses
    from app.services.category_service import get_category_tree

    alerts = get_low_stock_alerts(db, admin)
    RED = sum(1 for a in alerts if a.indicator == "RED")
    YELLOW = sum(1 for a in alerts if a.indicator == "YELLOW")
    GREEN = sum(1 for a in alerts if a.indicator == "GREEN")
    print(f"    Low-stock alerts : {len(alerts)} items (RED={RED}, YELLOW={YELLOW}, GREEN={GREEN})")

    movements = get_stock_movements(db)
    print(f"    Stock movements  : {len(movements)} records")

    turnover = calculate_inventory_turnover(db, admin)
    print(f"    Turnover rate    : {turnover.overall_turnover_rate} (Calculated over real transactions)")

    replen = calculate_replenishment_recommendations(db, admin)
    CRIT = sum(1 for r in replen if r.urgency == "CRITICAL")
    HIGH = sum(1 for r in replen if r.urgency == "HIGH")
    print(f"    Replenishment    : {len(replen)} items (CRITICAL={CRIT}, HIGH={HIGH})")

    warehouses = get_all_warehouses(db)
    print(f"    Warehouses       : {len(warehouses)} registered facilities")

    cat_tree = get_category_tree(db)
    print(f"    Category tree    : {len(cat_tree)} root categories")
    print(f"    Status           : ALL PASS")
except Exception as e:
    print(f"    ERROR: {e}")
    import traceback; traceback.print_exc()

print("\n" + "=" * 65)
db.close()
