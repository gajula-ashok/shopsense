from typing import List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.vendor import Vendor, VendorStatus
from app.models.user import User, UserRole
from app.models.transaction import Transaction
from app.schemas.vendor import VendorCreate, VendorUpdate, VendorResponse, VendorApplicationReview
from app.utils.validators import (
    validate_vendor_registration,
    validate_business_name,
    validate_owner_name,
    validate_phone_number,
    validate_category,
)

def create_vendor(db: Session, data: VendorCreate, current_user: User) -> Vendor:
    # 1. Run rigorous vendor registration validation
    payload = data.model_dump()
    errors = validate_vendor_registration(payload)
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"errors": errors}
        )

    # 2. Check for duplicate vendor email
    norm_email = data.email.strip().lower()
    existing = db.query(Vendor).filter(Vendor.email == norm_email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A vendor with email '{norm_email}' is already registered."
        )

    # 3. Determine user_id linkage and enforce role restrictions
    assigned_user_id = None
    if current_user.role == UserRole.ADMIN:
        assigned_user_id = data.user_id
        commission = data.commission_rate if data.commission_rate is not None else Decimal("10.00")
        new_status = data.status or VendorStatus.ACTIVE
        app_status = "APPROVED" if new_status == VendorStatus.ACTIVE else "PENDING"
    elif current_user.role == UserRole.VENDOR:
        if current_user.vendor:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Your account already has a vendor profile."
            )
        assigned_user_id = current_user.user_id
        commission = Decimal("10.00")
        new_status = VendorStatus.PENDING
        app_status = "PENDING"
    else:
        commission = Decimal("10.00")
        new_status = VendorStatus.PENDING
        app_status = "PENDING"

    # 4. Create vendor
    vendor = Vendor(
        business_name=data.business_name.strip(),
        owner_name=data.owner_name.strip(),
        email=norm_email,
        phone=data.phone.strip(),
        category=data.category.strip(),
        commission_rate=commission,
        status=new_status,
        user_id=assigned_user_id,
        business_address=data.business_address,
        city=data.city,
        state=data.state,
        pincode=data.pincode,
        tax_id=data.tax_id,
        application_status=app_status,
        review_notes="Application submitted by seller."
    )
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor

def get_vendors(
    db: Session,
    current_user: User,
    search: Optional[str] = None,
    category: Optional[str] = None,
    status_filter: Optional[str] = None,
    application_status: Optional[str] = None
) -> List[Vendor]:
    query = db.query(Vendor)

    # Item 1: VENDOR can ONLY view their own record; ADMIN views all
    if current_user.role == UserRole.VENDOR:
        if not current_user.vendor:
            return []
        return [current_user.vendor]

    # Admin filtering:
    if search:
        kw = f"%{search.strip().lower()}%"
        from sqlalchemy import or_, cast, String
        query = query.filter(
            or_(
                Vendor.business_name.ilike(kw),
                Vendor.owner_name.ilike(kw),
                Vendor.email.ilike(kw),
                cast(Vendor.vendor_id, String).ilike(kw)
            )
        )

    if category and category != "All":
        query = query.filter(Vendor.category == category)

    if status_filter and status_filter != "All":
        try:
            enum_status = VendorStatus(status_filter)
            query = query.filter(Vendor.status == enum_status)
        except ValueError:
            pass

    if application_status and application_status != "All":
        query = query.filter(Vendor.application_status == application_status)

    return query.order_by(Vendor.vendor_id.asc()).all()

def get_vendor_by_id(db: Session, vendor_id: int, current_user: User) -> Vendor:
    vendor = db.query(Vendor).filter(Vendor.vendor_id == vendor_id).first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with ID {vendor_id} not found."
        )

    # Item 1: VENDOR cannot view another vendor's profile
    if current_user.role == UserRole.VENDOR:
        if not current_user.vendor or current_user.vendor.vendor_id != vendor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: you may only view your own vendor profile."
            )

    return vendor

def review_vendor_application(db: Session, vendor_id: int, review: VendorApplicationReview, current_user: User) -> Vendor:
    """Administrator review action: APPROVE, REQUEST_INFO, or REJECT."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can review vendor applications."
        )

    vendor = db.query(Vendor).filter(Vendor.vendor_id == vendor_id).first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor application with ID {vendor_id} not found."
        )

    act = review.action.upper()
    notes = review.notes or ""

    if act == "APPROVE":
        vendor.application_status = "APPROVED"
        vendor.status = VendorStatus.ACTIVE
        vendor.review_notes = f"Approved by Admin: {notes}" if notes else "Application verified and approved. Active marketplace seller."
        # If user account is linked, ensure user is active
        if vendor.user:
            vendor.user.is_active = True
    elif act in ["REQUEST_INFO", "MORE_INFO_NEEDED"]:
        vendor.application_status = "MORE_INFO_NEEDED"
        vendor.status = VendorStatus.PENDING
        vendor.review_notes = f"Information Requested: {notes}" if notes else "Administrator requested additional verification documents."
    elif act == "REJECT":
        vendor.application_status = "REJECTED"
        vendor.status = VendorStatus.SUSPENDED
        vendor.review_notes = f"Application Rejected: {notes}" if notes else "Application rejected by marketplace administration."
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid action '{review.action}'. Must be APPROVE, REQUEST_INFO, or REJECT."
        )

    db.commit()
    db.refresh(vendor)
    return vendor

def update_vendor(db: Session, vendor_id: int, data: VendorUpdate, current_user: User) -> Vendor:
    vendor = db.query(Vendor).filter(Vendor.vendor_id == vendor_id).first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with ID {vendor_id} not found."
        )

    update_dict = data.model_dump(exclude_unset=True)

    if current_user.role == UserRole.VENDOR:
        if not current_user.vendor or current_user.vendor.vendor_id != vendor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: you may only modify your own vendor profile."
            )
        if "status" in update_dict and update_dict["status"] is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vendors are not permitted to alter their own operational status."
            )
        if "commission_rate" in update_dict and update_dict["commission_rate"] is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vendors cannot modify commission rates."
            )
        if "application_status" in update_dict:
            del update_dict["application_status"]

    field_errors = []

    if "business_name" in update_dict and update_dict["business_name"] is not None:
        ok, msg = validate_business_name(update_dict["business_name"])
        if not ok:
            field_errors.append(msg)

    if "owner_name" in update_dict and update_dict["owner_name"] is not None:
        ok, msg = validate_owner_name(update_dict["owner_name"])
        if not ok:
            field_errors.append(msg)

    if "phone" in update_dict and update_dict["phone"] is not None:
        ok, msg = validate_phone_number(update_dict["phone"])
        if not ok:
            field_errors.append(msg)

    if "category" in update_dict and update_dict["category"] is not None:
        ok, msg = validate_category(update_dict["category"])
        if not ok:
            field_errors.append(msg)

    if field_errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"errors": field_errors}
        )

    if "email" in update_dict and update_dict["email"]:
        new_email = update_dict["email"].strip().lower()
        if new_email != vendor.email:
            existing = db.query(Vendor).filter(Vendor.email == new_email).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Email '{new_email}' is already in use by another vendor."
                )
            vendor.email = new_email

    for key, val in update_dict.items():
        if key != "email" and hasattr(vendor, key) and val is not None:
            setattr(vendor, key, val)

    db.commit()
    db.refresh(vendor)
    return vendor

def delete_vendor(db: Session, vendor_id: int, current_user: User) -> dict:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete vendors."
        )

    vendor = db.query(Vendor).filter(Vendor.vendor_id == vendor_id).first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with ID {vendor_id} not found."
        )

    if db.query(Transaction).filter(Transaction.vendor_id == vendor_id).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This vendor has sales history and cannot be deleted. Suspend the vendor instead."
        )

    db.delete(vendor)
    db.commit()
    return {"message": f"Vendor {vendor_id} successfully deleted."}
