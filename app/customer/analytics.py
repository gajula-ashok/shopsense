import os
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.models.user import User, UserRole
from app.models.product import Product
from app.schemas.customer_recommendation import CustomerBehaviorSummary

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "transactions.csv")

def _load_transactions_df(db: Session) -> pd.DataFrame:
    """Load transactions with customer details from DB or dataset CSV."""
    db_txs = db.query(
        Transaction.transaction_id,
        Transaction.user_id,
        Transaction.product_id,
        Transaction.quantity,
        Transaction.amount,
        Transaction.transaction_date
    ).all()

    if len(db_txs) >= 40:
        df = pd.DataFrame(db_txs, columns=[
            "transaction_id", "customer_id", "product_id", "quantity", "amount", "transaction_date"
        ])
        df["customer_id"] = df["customer_id"].fillna(1).astype(int)
        df["quantity"] = df["quantity"].astype(int)
        df["amount"] = df["amount"].astype(float)
        df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    elif os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
    else:
        # Minimal synthetic generator
        np.random.seed(42)
        records = []
        for i in range(1, 150):
            records.append({
                "transaction_id": i,
                "customer_id": int(np.random.randint(1, 40)),
                "product_id": int(np.random.randint(1, 25)),
                "quantity": int(np.random.randint(1, 4)),
                "amount": float(round(np.random.uniform(25.0, 300.0), 2)),
                "transaction_date": (datetime.now() - pd.Timedelta(days=int(np.random.randint(1, 180)))).strftime("%Y-%m-%d %H:%M:%S")
            })
        df = pd.DataFrame(records)

    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    return df

import time as _t

_CUST_CACHE = {}
_CUST_CACHE_TIME = {}
_CUST_TTL = 3.0

def get_customer_behavior_metrics(db: Session, target_customer_id: Optional[int] = None) -> List[CustomerBehaviorSummary]:
    """
    Optimized Customer Behavior Analysis with lightweight short TTL cache.
    """
    cache_key = target_customer_id or 0
    if cache_key in _CUST_CACHE and (_t.time() - _CUST_CACHE_TIME.get(cache_key, 0) < _CUST_TTL):
        return _CUST_CACHE[cache_key]

    df = _load_transactions_df(db)

    # Product names map
    prods = db.query(Product.product_id, Product.product_name).all()
    prod_name_map = {p[0]: p[1] for p in prods}

    # Customers map
    users = db.query(User.user_id, User.full_name, User.email).filter(User.role == UserRole.CUSTOMER).all()
    user_map = {u[0]: (u[1], u[2]) for u in users}

    if target_customer_id:
        df = df[df["customer_id"] == target_customer_id]
        if df.empty:
            return []

    # Single-pass grouped aggregations
    grouped = df.groupby("customer_id")
    agg_df = grouped.agg(
        total_orders=("transaction_id", "count"),
        total_spent=("amount", "sum"),
        average_order_value=("amount", "mean"),
        first_purchase_date=("transaction_date", "min"),
        last_purchase_date=("transaction_date", "max")
    ).reset_index()

    # Precompute top products per customer
    cust_prod_qty = df.groupby(["customer_id", "product_id"])["quantity"].sum().reset_index()
    cust_top_prods = cust_prod_qty.sort_values(["customer_id", "quantity"], ascending=[True, False]).groupby("customer_id").head(3)
    prod_dict_per_cust = {}
    for cid, sub in cust_top_prods.groupby("customer_id"):
        prod_dict_per_cust[cid] = [
            {"product_id": int(r.product_id), "product_name": prod_name_map.get(r.product_id, f"Product #{r.product_id}"), "quantity_bought": int(r.quantity)}
            for r in sub.itertuples()
        ]

    now = datetime.now()
    summaries = []

    for row in agg_df.itertuples():
        cid = row.customer_id
        tot_orders = row.total_orders
        tot_spent = round(float(row.total_spent), 2)
        avg_ov = round(float(row.average_order_value), 2)
        first_dt = row.first_purchase_date
        last_dt = row.last_purchase_date
        span_days = max(1, (last_dt - first_dt).days)
        freq_days = round(span_days / max(1, tot_orders), 1)

        days_since_last = (now - last_dt).days
        if days_since_last <= 45:
            activity = "ACTIVE"
        elif days_since_last <= 120:
            activity = "OCCASIONAL"
        else:
            activity = "DORMANT"

        name, email = user_map.get(cid, (f"Customer #{cid}", f"customer{cid}@example.com"))

        summaries.append(CustomerBehaviorSummary(
            customer_id=int(cid),
            customer_name=name,
            email=email,
            total_orders=tot_orders,
            total_spent=tot_spent,
            average_order_value=avg_ov,
            purchase_frequency_days=freq_days,
            most_purchased_products=prod_dict_per_cust.get(cid, []),
            first_purchase_date=first_dt.strftime("%Y-%m-%d"),
            last_purchase_date=last_dt.strftime("%Y-%m-%d"),
            activity_status=activity
        ))

    summaries.sort(key=lambda x: x.total_spent, reverse=True)
    _CUST_CACHE[cache_key] = summaries
    _CUST_CACHE_TIME[cache_key] = _t.time()
    return summaries
