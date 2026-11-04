from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.schemas.customer_recommendation import (
    CustomerRecommendationResponse,
    RecommendationEvaluation
)
from app.recommendation.recommendation import recommend_products, evaluate_recommendations
from app.utils.security import get_current_active_user
from app.models.user import User, UserRole

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])

@router.get("/evaluation", response_model=RecommendationEvaluation)
def get_recommendation_evaluation(
    k: int = Query(5, ge=1, le=10),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Evaluate recommendation precision: Precision@K with target >= 75%."""
    return evaluate_recommendations(db, k=k)

@router.get("/{customer_id}", response_model=CustomerRecommendationResponse)
def get_recommendations_for_customer(
    customer_id: int,
    top_n: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Personalized product recommendations for a customer using collaborative filtering.
    Customers may view their own recommendations; Admins and Vendors can query any customer.
    """
    # Enforce customer self-access restriction if role is CUSTOMER
    if current_user.role == UserRole.CUSTOMER and current_user.user_id != customer_id:
        customer_id = current_user.user_id

    return recommend_products(db, customer_id=customer_id, top_n=top_n)
