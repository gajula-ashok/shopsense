from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
from app.models.transaction import Transaction
from app.models.product import Product
from app.models.vendor import Vendor
from app.models.inventory import Inventory
from app.models.user import User, UserRole
from app.services.analytics_service import _get_scoped_dataframes

import time as _t

_REVENUE_CACHE = {}
_REVENUE_CACHE_TIME = {}
_CACHE_TTL = 3.0  # 3 seconds TTL for sub-second rapid repeated hits

def calculate_advanced_revenue(
    db: Session,
    current_user: User,
    vendor_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Computes:
    - GMV (Gross Merchandise Value)
    - Total Marketplace Revenue
    - Total Orders & Quantity
    - Average Order Value (AOV)
    - Monthly Revenue Breakdown & Growth Rates
    - Vendor Rankings & Benchmarks
    - Top Selling Products
    - Category-wise Revenue Breakdown
    """
    cache_key = (current_user.user_id, current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role), vendor_id)
    if cache_key in _REVENUE_CACHE:
        if _t.time() - _REVENUE_CACHE_TIME.get(cache_key, 0) < _CACHE_TTL:
            return _REVENUE_CACHE[cache_key]

    dfs = _get_scoped_dataframes(db, current_user, vendor_id)
    df_t = dfs["transactions"].copy()
    df_p = dfs["products"].copy()
    df_v = dfs["vendors"].copy()

    if df_t.empty:
        return {
            "gmv": 0.0,
            "total_revenue": 0.0,
            "total_orders": 0,
            "total_units_sold": 0,
            "aov": 0.0,
            "monthly_revenue": [],
            "growth_rate_pct": 0.0,
            "top_vendors": [],
            "top_products": [],
            "category_revenue": []
        }

    total_revenue = round(float(df_t["amount"].sum()), 2)
    # In this multi-vendor context, transaction amount reflects the GMV transacted
    gmv = total_revenue
    total_orders = int(len(df_t))
    total_units_sold = int(df_t["quantity"].sum())
    aov = round(total_revenue / max(1, total_orders), 2)

    # Monthly revenue & growth rate
    df_t["year_month"] = df_t["transaction_date"].dt.strftime("%Y-%m")
    m_grp = df_t.groupby("year_month").agg(
        revenue=("amount", "sum"),
        orders=("transaction_id", "count"),
        units=("quantity", "sum")
    ).reset_index().sort_values(by="year_month")

    m_grp["revenue"] = m_grp["revenue"].round(2)
    m_grp["growth_pct"] = m_grp["revenue"].pct_change().fillna(0.0).mul(100).round(2)
    monthly_revenue = m_grp.to_dict(orient="records")

    latest_growth = float(monthly_revenue[-1]["growth_pct"]) if len(monthly_revenue) > 1 else 0.0

    # Vendor rankings
    v_agg = df_t.groupby("vendor_id").agg(
        revenue=("amount", "sum"),
        orders=("transaction_id", "count"),
        units_sold=("quantity", "sum")
    ).reset_index()

    v_merged = df_v.merge(v_agg, on="vendor_id", how="left")
    v_merged["revenue"] = v_merged["revenue"].fillna(0.0).round(2)
    v_merged["orders"] = v_merged["orders"].fillna(0).astype(int)
    v_merged["units_sold"] = v_merged["units_sold"].fillna(0).astype(int)
    v_merged["market_share_pct"] = (v_merged["revenue"] / max(1.0, total_revenue) * 100).round(2)
    v_merged = v_merged.sort_values(by="revenue", ascending=False).reset_index(drop=True)
    v_merged["rank"] = v_merged.index + 1
    top_vendors = v_merged.head(10).to_dict(orient="records")

    # Top selling products
    p_agg = df_t.groupby("product_id").agg(
        revenue=("amount", "sum"),
        units_sold=("quantity", "sum")
    ).reset_index()

    p_merged = df_p.merge(p_agg, on="product_id", how="left")
    p_merged["revenue"] = p_merged["revenue"].fillna(0.0).round(2)
    p_merged["units_sold"] = p_merged["units_sold"].fillna(0).astype(int)
    p_merged = p_merged.sort_values(by="revenue", ascending=False).reset_index(drop=True)
    top_products = p_merged.head(10).to_dict(orient="records")

    # Category revenue
    c_agg = df_t.groupby("category").agg(
        revenue=("amount", "sum"),
        units_sold=("quantity", "sum"),
        order_count=("transaction_id", "count")
    ).reset_index()
    c_agg["revenue"] = c_agg["revenue"].round(2)
    c_agg["revenue_share_pct"] = (c_agg["revenue"] / max(1.0, total_revenue) * 100).round(2)
    category_revenue = c_agg.sort_values(by="revenue", ascending=False).to_dict(orient="records")

    result = {
        "gmv": gmv,
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "total_units_sold": total_units_sold,
        "aov": aov,
        "monthly_revenue": monthly_revenue,
        "growth_rate_pct": latest_growth,
        "top_vendors": top_vendors,
        "top_products": top_products,
        "category_revenue": category_revenue
    }
    _REVENUE_CACHE[cache_key] = result
    _REVENUE_CACHE_TIME[cache_key] = _t.time()
    return result
