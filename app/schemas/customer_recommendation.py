from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class CustomerBehaviorSummary(BaseModel):
    customer_id: int
    customer_name: str
    email: str
    total_orders: int
    total_spent: float
    average_order_value: float
    purchase_frequency_days: float
    most_purchased_products: List[Dict[str, Any]]
    first_purchase_date: Optional[str] = None
    last_purchase_date: Optional[str] = None
    activity_status: str  # ACTIVE, OCCASIONAL, DORMANT

class CustomerSegmentStats(BaseModel):
    segment_name: str
    count: int
    percentage: float
    avg_spent: float
    avg_orders: float
    avg_order_value: float
    description: str

class CustomerSegmentationResponse(BaseModel):
    silhouette_score: float
    optimal_clusters: int
    evaluation_target: str = "Silhouette Score >= 0.85"
    target_met: bool
    segment_summary: List[CustomerSegmentStats]
    customer_records: List[Dict[str, Any]]

class RecommendationItem(BaseModel):
    product_id: int
    product_name: str
    category: str
    price: float
    score: float
    reason: str

class RecommendationEvaluation(BaseModel):
    precision_at_k: float
    precision_target: float = 0.75
    target_met: bool
    k: int
    total_customers_evaluated: int
    evaluation_method: str = "Leave-One-Out / User-Split Collaborative Precision@K"

class CustomerRecommendationResponse(BaseModel):
    customer_id: int
    customer_name: str
    recommendations: List[RecommendationItem]
    top_n: int
