from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.category import Category
from app.models.product import Product
from app.models.user import User, UserRole
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryTreeResponse

def get_all_categories(db: Session) -> List[dict]:
    cats = db.query(Category).order_by(Category.category_id.asc()).all()
    id_to_name = {c.category_id: c.category_name for c in cats}
    res = []
    for c in cats:
        prod_count = db.query(Product).filter(Product.category == c.category_name).count()
        res.append({
            "category_id": c.category_id,
            "category_name": c.category_name,
            "parent_id": c.parent_id,
            "parent_name": id_to_name.get(c.parent_id) if c.parent_id else None,
            "description": c.description,
            "product_count": prod_count,
            "created_at": c.created_at
        })
    return res

def get_category_tree(db: Session) -> List[dict]:
    cats = db.query(Category).order_by(Category.category_id.asc()).all()
    # Build tree
    lookup = {c.category_id: {"category_id": c.category_id, "category_name": c.category_name, "description": c.description, "subcategories": []} for c in cats}
    roots = []
    for c in cats:
        if c.parent_id and c.parent_id in lookup:
            lookup[c.parent_id]["subcategories"].append(lookup[c.category_id])
        else:
            roots.append(lookup[c.category_id])
    return roots

def create_category(db: Session, payload: CategoryCreate, current_user: User) -> Category:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Marketplace Administrators can create categories."
        )

    existing = db.query(Category).filter(Category.category_name == payload.category_name.strip()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Category '{payload.category_name}' already exists."
        )

    cat = Category(
        category_name=payload.category_name.strip(),
        parent_id=payload.parent_id,
        description=payload.description
    )
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat

def update_category(db: Session, category_id: int, payload: CategoryUpdate, current_user: User) -> Category:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Marketplace Administrators can update categories."
        )

    cat = db.query(Category).filter(Category.category_id == category_id).first()
    if not cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category #{category_id} not found."
        )

    if payload.category_name is not None and payload.category_name.strip():
        new_name = payload.category_name.strip()
        if new_name != cat.category_name:
            dup = db.query(Category).filter(Category.category_name == new_name).first()
            if dup:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Category '{new_name}' already exists.")
            old_name = cat.category_name
            cat.category_name = new_name
            # Update product category strings
            db.query(Product).filter(Product.category == old_name).update({"category": new_name})

    if payload.parent_id is not None:
        if payload.parent_id == category_id:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="A category cannot be its own parent.")
        cat.parent_id = payload.parent_id

    if payload.description is not None:
        cat.description = payload.description

    db.commit()
    db.refresh(cat)
    return cat
