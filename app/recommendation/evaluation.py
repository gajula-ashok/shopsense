"""
Recommendation Engine Evaluation module
Calculates Precision@K and evaluates collaborative filtering model performance.
"""
from app.recommendation.recommendation import evaluate_recommendations

__all__ = ["evaluate_recommendations"]
