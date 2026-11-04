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
        records = [
            {
                "transaction_id": t.transaction_id,
                "customer_id": t.user_id or 1,
                "product_id": t.product_id,
                "quantity": t.quantity,
                "amount": float(t.amount),
                "transaction_date": t.transaction_date.strftime("%Y-%m-%d %H:%M:%S")
            }
            for t in db_txs
        ]
        df = pd.DataFrame(records)
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

def get_customer_behavior_metrics(db: Session, target_customer_id: Optional[int] = None) -> List[CustomerBehaviorSummary]:
    """
    Customer Behavior Analysis:
    1. Total orders per customer
    2. Total amount spent
    3. Average order value
    4. Purchase frequency (days between purchases)
    5. Most purchased products
    6. Customer purchase history and activity status
    """
    df = _load_transactions_df(db)

    # Product names map
    prods = db.query(Product.product_id, Product.product_name).all()
    prod_name_map = {p[0]: p[1] for p in prods}

    # Customers map
    users = db.query(User.user_id, User.full_name, User.email).filter(User.role == UserRole.CUSTOMER).all()
    user_map = {u[0]: (u[1], u[2]) for u in users}

    summaries = []
    customer_ids = df["customer_id"].unique()

    if target_customer_id:
        customer_ids = [target_customer_id]

    now = datetime.now()

    for cid in customer_ids:
        c_df = df[df["customer_id"] == cid]
        if c_df.empty:
            continue

        total_orders = len(c_df)
        total_spent = round(float(c_df["amount"].sum()), 2)
        avg_order_val = round(float(c_df["amount"].mean()), 2)

        # Date analysis
        sorted_dates = c_df["transaction_date"].sort_values()
        first_dt = sorted_dates.iloc[0]
        last_dt = sorted_dates.iloc[-1]
        date_span_days = max(1, (last_dt - first_dt).days)
        freq_days = round(date_span_days / max(1, total_orders), 1)

        # Most purchased products
        top_prods_s = c_df.groupby("product_id")["quantity"].sum().sort_values(ascending=False).head(3)
        top_prods = [
            {"product_id": int(pid), "product_name": prod_name_map.get(pid, f"Product #{pid}"), "quantity_bought": int(qty)}
            for pid, qty in top_prods_s.items()
        ]

        # Activity status
        days_since_last = (now - last_dt).days
        if days_since_last <= 45:
            activity = "ACTIVE"
        elif days_since_last <= 120:
            activity = "OCCASIONAL"
        else:
            activity = "DORMANT"

        # Customer name / email
        name, email = user_map.get(cid, (f"Customer #{cid}", f"customer{cid}@example.com"))

        summaries.append(CustomerBehaviorSummary(
            customer_id=int(cid),
            customer_name=name,
            email=email,
            total_orders=total_orders,
            total_spent=total_spent,
            average_order_value=avg_order_val,
            purchase_frequency_days=freq_days,
            most_purchased_products=top_prods,
            first_purchase_date=first_dt.strftime("%Y-%m-%d"),
            last_purchase_date=last_dt.strftime("%Y-%m-%d"),
            activity_status=activity
        ))

    summaries.sort(key=lambda x: x.total_spent, reverse=True)
    return summaries
