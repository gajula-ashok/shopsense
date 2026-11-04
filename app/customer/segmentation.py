import os
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from app.customer.analytics import _load_transactions_df
from app.models.user import User, UserRole
from app.schemas.customer_recommendation import (
    CustomerSegmentationResponse,
    CustomerSegmentStats
)

def perform_customer_segmentation(db: Session, n_clusters: Optional[int] = None) -> CustomerSegmentationResponse:
    """
    Customer Segmentation Using K-Means Clustering on RFM & AOV metrics.
    Features: Total Orders (Frequency), Total Spent (Monetary), Average Order Value (AOV), Purchase Frequency.
    Scale: StandardScaler.
    Silhouette Score evaluated dynamically across candidate cluster counts k=2..6.
    Cluster labels dynamically assigned based on actual spending and order patterns.
    """
    df = _load_transactions_df(db)

    # Calculate customer feature matrix
    records = []
    users = db.query(User.user_id, User.full_name, User.email).filter(User.role == UserRole.CUSTOMER).all()
    user_map = {u[0]: (u[1], u[2]) for u in users}

    for cid, c_df in df.groupby("customer_id"):
        tot_orders = len(c_df)
        tot_spent = float(c_df["amount"].sum())
        avg_ov = float(c_df["amount"].mean())
        dates = c_df["transaction_date"].sort_values()
        span_days = max(1, (dates.iloc[-1] - dates.iloc[0]).days)
        freq = float(span_days / max(1, tot_orders))

        name, email = user_map.get(cid, (f"Customer #{cid}", f"customer{cid}@example.com"))

        records.append({
            "customer_id": int(cid),
            "customer_name": name,
            "email": email,
            "total_orders": tot_orders,
            "total_spent": tot_spent,
            "avg_order_value": avg_ov,
            "purchase_frequency": freq
        })

    feat_df = pd.DataFrame(records)

    features = ["total_orders", "total_spent", "avg_order_value", "purchase_frequency"]
    X = feat_df[features].fillna(0)

    # Scale numerical features using StandardScaler
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Auto-select best k via Silhouette analysis if not explicitly provided or if n_clusters <= 0
    if n_clusters is None or n_clusters < 2:
        best_k = 4
        best_sil = -1.0
        for k in range(2, 7):
            km = KMeans(n_clusters=k, random_state=42, n_init=15)
            labels = km.fit_predict(X_scaled)
            score = float(silhouette_score(X_scaled, labels))
            if score > best_sil:
                best_sil = score
                best_k = k
        selected_k = best_k
    else:
        selected_k = n_clusters

    # Apply K-Means with selected_k
    kmeans = KMeans(n_clusters=selected_k, random_state=42, n_init=15)
    cluster_labels = kmeans.fit_predict(X_scaled)
    feat_df["cluster"] = cluster_labels

    # Calculate Silhouette Score
    if len(np.unique(cluster_labels)) > 1:
        sil_score = float(silhouette_score(X_scaled, cluster_labels))
    else:
        sil_score = 0.0

    # Dynamically assign meaningful segment labels based on actual cluster characteristics
    # Sort clusters by average total_spent ascending
    cluster_means = feat_df.groupby("cluster")["total_spent"].mean().sort_values()
    sorted_cluster_ids = list(cluster_means.index)

    cluster_to_label = {}
    if len(sorted_cluster_ids) == 2:
        cluster_to_label[sorted_cluster_ids[0]] = (
            "BUDGET & OCCASIONAL SHOPPERS",
            "Lower order frequency and lifetime spend. Price-conscious customer base."
        )
        cluster_to_label[sorted_cluster_ids[1]] = (
            "HIGH VALUE & FREQUENT BUYERS",
            "Consistent purchases, high average order values, and strong brand engagement."
        )
    elif len(sorted_cluster_ids) == 3:
        cluster_to_label[sorted_cluster_ids[0]] = (
            "LOW ACTIVITY CUSTOMERS",
            "Fewer purchases, lower lifetime spending, price-sensitive shoppers."
        )
        cluster_to_label[sorted_cluster_ids[1]] = (
            "REGULAR CUSTOMERS",
            "Moderate purchase frequency, consistent spending and steady loyalty."
        )
        cluster_to_label[sorted_cluster_ids[2]] = (
            "HIGH VALUE CUSTOMERS",
            "Frequent repeat purchases, premium spending and highest average order values."
        )
    elif len(sorted_cluster_ids) == 4:
        cluster_to_label[sorted_cluster_ids[0]] = (
            "AT-RISK / LOW ACTIVITY",
            "Infrequent visits with minimal basket sizes; candidates for reactivation campaigns."
        )
        cluster_to_label[sorted_cluster_ids[1]] = (
            "BUDGET SHOPPERS",
            "Moderate order frequency seeking deals and entry-level products."
        )
        cluster_to_label[sorted_cluster_ids[2]] = (
            "LOYAL CORE CUSTOMERS",
            "Consistent order patterns, healthy order volumes, and high repeat intent."
        )
        cluster_to_label[sorted_cluster_ids[3]] = (
            "HIGH VALUE VIPs",
            "Top lifetime spenders with premium order values driving key revenue."
        )
    else:
        # Generic graceful fallback for k >= 5
        for idx, c_id in enumerate(sorted_cluster_ids):
            tier_pct = round(((idx + 1) / len(sorted_cluster_ids)) * 100)
            cluster_to_label[c_id] = (
                f"TIER {idx + 1} - SPEND PERCENTILE {tier_pct}%",
                f"Clustered customer group with average spend ${round(cluster_means[c_id], 2)}."
            )

    feat_df["segment_name"] = feat_df["cluster"].map(lambda c: cluster_to_label[c][0])

    # Build summary stats
    segment_summaries = []
    total_custs = len(feat_df)
    for c_id in sorted_cluster_ids:
        lbl, desc = cluster_to_label[c_id]
        c_sub = feat_df[feat_df["cluster"] == c_id]
        segment_summaries.append(CustomerSegmentStats(
            segment_name=lbl,
            count=len(c_sub),
            percentage=round((len(c_sub) / total_custs) * 100, 1),
            avg_spent=round(float(c_sub["total_spent"].mean()), 2),
            avg_orders=round(float(c_sub["total_orders"].mean()), 1),
            avg_order_value=round(float(c_sub["avg_order_value"].mean()), 2),
            description=desc
        ))

    # Return customer records
    customer_records = []
    for _, row in feat_df.iterrows():
        customer_records.append({
            "customer_id": int(row["customer_id"]),
            "customer_name": row["customer_name"],
            "email": row["email"],
            "total_orders": int(row["total_orders"]),
            "total_spent": round(float(row["total_spent"]), 2),
            "avg_order_value": round(float(row["avg_order_value"]), 2),
            "purchase_frequency": round(float(row["purchase_frequency"]), 1),
            "segment_name": row["segment_name"]
        })

    # The practical target for real uniform-continuous RFM distributions is >= 0.35
    target_met = sil_score >= 0.35

    return CustomerSegmentationResponse(
        silhouette_score=round(sil_score, 4),
        optimal_clusters=selected_k,
        evaluation_target="Silhouette Score >= 0.35 (Real-World RFM)",
        target_met=target_met,
        segment_summary=segment_summaries,
        customer_records=customer_records
    )
