from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryTreeResponse
from app.services import category_service
from app.utils.security import get_current_active_user, require_admin
from app.models.user import User

router = APIRouter(prefix="/api/categories", tags=["Categories"])

@router.get("", response_model=List[dict])
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all categories with parent names and product counts."""
    return category_service.get_all_categories(db)

@router.get("/tree", response_model=List[dict])
def list_category_tree(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get nested hierarchical category tree."""
    return category_service.get_category_tree(db)

@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def add_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new category or subcategory (Admin only)."""
    return category_service.create_category(db, payload, current_user)

@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update category name, description, or parent hierarchy."""
    return category_service.update_category(db, category_id, payload, current_user)
