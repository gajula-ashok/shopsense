import pytest
from app.models.warehouse import Warehouse
from app.models.category import Category
from app.models.vendor import Vendor, VendorStatus
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.interaction import ProductInteraction

def _get_or_create_vendor(db):
    v = db.query(Vendor).first()
    if not v:
        v = Vendor(business_name="Test Vendor Ltd", owner_name="Vendor Owner", email="vowner@example.com", phone="9876543210", category="Electronics", status=VendorStatus.ACTIVE)
        db.add(v)
        db.commit()
        db.refresh(v)
    return v

def test_milestone2_warehouses_and_categories_endpoints(client, admin_token, vendor_token, db):
    wh = Warehouse(warehouse_name="Test Central Hub", location="Chicago, IL", capacity=10000)
    cat = Category(category_name="Electronics", description="Gadgets")
    db.add(wh)
    db.add(cat)
    db.commit()

    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    headers_vendor = {"Authorization": f"Bearer {vendor_token}"}

    # 1. Get warehouses
    res_wh = client.get("/api/warehouses", headers=headers_admin)
    assert res_wh.status_code == 200
    warehouses = res_wh.json()
    assert len(warehouses) >= 1
    assert warehouses[0]["warehouse_name"] == "Test Central Hub"
    assert "capacity" in warehouses[0]
    assert "utilization_percentage" in warehouses[0]

    # 2. Get categories tree
    res_cat = client.get("/api/categories/tree", headers=headers_vendor)
    assert res_cat.status_code == 200
    tree = res_cat.json()
    assert len(tree) >= 1
    assert tree[0]["category_name"] == "Electronics"
    assert "subcategories" in tree[0]

def test_milestone2_inventory_intelligence_endpoints(client, admin_token, db):
    vendor = _get_or_create_vendor(db)
    prod = Product(product_name="Test Headset Pro", category="Electronics", price=99.99, stock=5, vendor_id=vendor.vendor_id)
    db.add(prod)
    db.commit()
    db.refresh(prod)

    inv = Inventory(product_id=prod.product_id, current_stock=5, reorder_level=10, warehouse="Test Central Hub")
    db.add(inv)
    db.commit()

    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Low stock alerts
    res_alerts = client.get("/api/inventory/alerts", headers=headers)
    assert res_alerts.status_code == 200
    alerts = res_alerts.json()
    assert len(alerts) >= 1
    assert alerts[0]["indicator"] in ["GREEN", "YELLOW", "RED"]

    # 2. Turnover analytics
    res_turn = client.get("/api/inventory/turnover", headers=headers)
    assert res_turn.status_code == 200
    turn_data = res_turn.json()
    assert "overall_turnover_rate" in turn_data
    assert "total_cogs" in turn_data

    # 3. Demand Forecasting (ML Random Forest)
    res_fc = client.get("/api/inventory/forecast", headers=headers)
    assert res_fc.status_code == 200
    fc_data = res_fc.json()
    assert "forecasts" in fc_data
    assert "evaluation" in fc_data
    eval_metrics = fc_data["evaluation"]
    assert "mae" in eval_metrics
    assert "rmse" in eval_metrics
    assert "accuracy_percentage" in eval_metrics
    assert eval_metrics["accuracy_percentage"] >= 0.0

    # 4. Replenishment recommendations
    res_rep = client.get("/api/inventory/replenishment", headers=headers)
    assert res_rep.status_code == 200
    rep_list = res_rep.json()
    assert len(rep_list) >= 1
    assert "recommended_reorder_qty" in rep_list[0]
    assert "target_stock_level" in rep_list[0]
    assert rep_list[0]["urgency"] in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

def test_milestone2_customer_analytics_and_segmentation(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Customer behavior metrics
    res_cust = client.get("/api/analytics/customers", headers=headers)
    assert res_cust.status_code == 200
    cust_data = res_cust.json()
    assert len(cust_data) >= 1
    assert "total_orders" in cust_data[0]
    assert "total_spent" in cust_data[0]
    assert "average_order_value" in cust_data[0]
    assert "purchase_frequency_days" in cust_data[0]

    # 2. Customer segmentation via K-Means
    res_seg = client.get("/api/analytics/segments?n_clusters=3", headers=headers)
    assert res_seg.status_code == 200
    seg_data = res_seg.json()
    assert "silhouette_score" in seg_data
    assert "optimal_clusters" in seg_data
    assert len(seg_data["segment_summary"]) == 3
    assert any("HIGH VALUE" in s["segment_name"] for s in seg_data["segment_summary"])
    assert any("REGULAR" in s["segment_name"] for s in seg_data["segment_summary"])
    assert any("LOW ACTIVITY" in s["segment_name"] for s in seg_data["segment_summary"])

def test_milestone2_recommendation_engine(client, admin_token, db):
    vendor = _get_or_create_vendor(db)
    for i in range(1, 7):
        p = Product(product_name=f"Catalog Item {i}", category="Electronics", price=49.99, stock=20, vendor_id=vendor.vendor_id)
        db.add(p)
    db.commit()

    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Top 5 recommendations for customer 1
    res_rec = client.get("/api/recommendations/1?top_n=5", headers=headers)
    assert res_rec.status_code == 200
    rec_data = res_rec.json()
    assert "recommendations" in rec_data
    assert len(rec_data["recommendations"]) == 5
    assert "score" in rec_data["recommendations"][0]
    assert "product_name" in rec_data["recommendations"][0]

    # 2. Recommendation Precision@K evaluation
    res_eval = client.get("/api/recommendations/evaluation?k=5", headers=headers)
    assert res_eval.status_code == 200
    eval_data = res_eval.json()
    assert "precision_at_k" in eval_data
    assert "precision_target" in eval_data
    assert eval_data["precision_at_k"] >= 0.0
