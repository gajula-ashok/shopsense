from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User, UserRole
from app.models.vendor import Vendor
from app.models.address import Address
from app.schemas.profile import (
    VendorProfileResponse,
    VendorProfileUpdate,
    CustomerProfileResponse,
    CustomerProfileUpdate,
    AddressCreate,
    AddressUpdate,
    AddressResponse
)

def get_vendor_profile(db: Session, current_user: User) -> VendorProfileResponse:
    if current_user.role != UserRole.VENDOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only vendors can access vendor profile")
    vendor = current_user.vendor
    if not vendor:
        vendor = db.query(Vendor).filter(Vendor.email == current_user.email).first()
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor profile not found")

    return VendorProfileResponse(
        vendor_id=vendor.vendor_id,
        user_id=current_user.user_id,
        full_name=current_user.full_name,
        email=current_user.email,
        phone=vendor.phone or current_user.phone or "",
        avatar_url=vendor.avatar_url or current_user.avatar_url,
        business_name=vendor.business_name,
        owner_name=vendor.owner_name,
        category=vendor.category,
        description=vendor.description,
        business_address=vendor.business_address,
        city=vendor.city,
        state=vendor.state,
        pincode=vendor.pincode,
        tax_id=vendor.tax_id,
        status=vendor.status.value if hasattr(vendor.status, 'value') else str(vendor.status),
        commission_rate=float(vendor.commission_rate),
        preferences=vendor.preferences or current_user.preferences or {},
        created_at=vendor.created_at
    )

def update_vendor_profile(db: Session, current_user: User, payload: VendorProfileUpdate) -> VendorProfileResponse:
    if current_user.role != UserRole.VENDOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only vendors can update vendor profile")
    vendor = current_user.vendor
    if not vendor:
        vendor = db.query(Vendor).filter(Vendor.email == current_user.email).first()
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor profile not found")

    # Update User model attributes
    if payload.full_name and payload.full_name.strip():
        current_user.full_name = payload.full_name.strip()
        vendor.owner_name = payload.full_name.strip()
    if payload.phone and payload.phone.strip():
        current_user.phone = payload.phone.strip()
        vendor.phone = payload.phone.strip()
    if payload.avatar_url is not None:
        current_user.avatar_url = payload.avatar_url
        vendor.avatar_url = payload.avatar_url

    # Update Vendor model attributes
    if payload.business_name and payload.business_name.strip():
        vendor.business_name = payload.business_name.strip()
    if payload.description is not None:
        vendor.description = payload.description.strip()
    if payload.business_address is not None:
        vendor.business_address = payload.business_address.strip()
    if payload.city is not None:
        vendor.city = payload.city.strip()
    if payload.state is not None:
        vendor.state = payload.state.strip()
    if payload.pincode is not None:
        vendor.pincode = payload.pincode.strip()
    if payload.preferences is not None:
        merged_prefs = dict(vendor.preferences or {})
        merged_prefs.update(payload.preferences)
        vendor.preferences = merged_prefs
        current_user.preferences = merged_prefs

    db.commit()
    db.refresh(current_user)
    db.refresh(vendor)

    return get_vendor_profile(db, current_user)

def get_customer_profile(db: Session, current_user: User) -> CustomerProfileResponse:
    addrs = db.query(Address).filter(Address.user_id == current_user.user_id).order_by(Address.is_default.desc(), Address.address_id.desc()).all()
    default_addr = next((a for a in addrs if a.is_default), addrs[0] if addrs else None)

    return CustomerProfileResponse(
        user_id=current_user.user_id,
        full_name=current_user.full_name,
        email=current_user.email,
        phone=current_user.phone or "",
        role=current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
        avatar_url=current_user.avatar_url,
        preferences=current_user.preferences or {"currency": "USD", "email_notifications": True, "sms_notifications": True, "order_notifications": True},
        default_address=AddressResponse.from_orm(default_addr) if default_addr else None,
        addresses=[AddressResponse.from_orm(a) for a in addrs],
        created_at=current_user.created_at
    )

def update_customer_profile(db: Session, current_user: User, payload: CustomerProfileUpdate) -> CustomerProfileResponse:
    if payload.full_name and payload.full_name.strip():
        current_user.full_name = payload.full_name.strip()
    if payload.phone and payload.phone.strip():
        current_user.phone = payload.phone.strip()
    if payload.avatar_url is not None:
        current_user.avatar_url = payload.avatar_url
    if payload.preferences is not None:
        merged_prefs = dict(current_user.preferences or {})
        merged_prefs.update(payload.preferences)
        current_user.preferences = merged_prefs

    db.commit()
    db.refresh(current_user)
    return get_customer_profile(db, current_user)

# Address Management
def list_user_addresses(db: Session, current_user: User) -> List[AddressResponse]:
    addrs = db.query(Address).filter(Address.user_id == current_user.user_id).order_by(Address.is_default.desc(), Address.address_id.desc()).all()
    return [AddressResponse.from_orm(a) for a in addrs]

def create_user_address(db: Session, current_user: User, payload: AddressCreate) -> AddressResponse:
    if payload.is_default:
        db.query(Address).filter(Address.user_id == current_user.user_id).update({"is_default": False})

    # If first address, make it default automatically
    existing_count = db.query(Address).filter(Address.user_id == current_user.user_id).count()
    is_def = payload.is_default or (existing_count == 0)

    addr = Address(
        user_id=current_user.user_id,
        recipient_name=payload.recipient_name.strip(),
        phone=payload.phone.strip(),
        house_building=payload.house_building.strip() if payload.house_building else "",
        street_address=payload.street_address.strip(),
        area_locality=payload.area_locality.strip() if payload.area_locality else "",
        city=payload.city.strip(),
        state=payload.state.strip(),
        pincode=payload.pincode.strip(),
        is_default=is_def,
        address_type=payload.address_type or "HOME"
    )
    db.add(addr)
    db.commit()
    db.refresh(addr)
    return AddressResponse.from_orm(addr)

def update_user_address(db: Session, current_user: User, address_id: int, payload: AddressUpdate) -> AddressResponse:
    addr = db.query(Address).filter(Address.address_id == address_id, Address.user_id == current_user.user_id).first()
    if not addr:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")

    if payload.is_default:
        db.query(Address).filter(Address.user_id == current_user.user_id).update({"is_default": False})
        addr.is_default = True

    for field, val in payload.dict(exclude_unset=True).items():
        if val is not None:
            setattr(addr, field, val)

    db.commit()
    db.refresh(addr)
    return AddressResponse.from_orm(addr)

def set_default_address(db: Session, current_user: User, address_id: int) -> AddressResponse:
    addr = db.query(Address).filter(Address.address_id == address_id, Address.user_id == current_user.user_id).first()
    if not addr:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")

    db.query(Address).filter(Address.user_id == current_user.user_id).update({"is_default": False})
    addr.is_default = True
    db.commit()
    db.refresh(addr)
    return AddressResponse.from_orm(addr)

def delete_user_address(db: Session, current_user: User, address_id: int) -> Dict[str, Any]:
    addr = db.query(Address).filter(Address.address_id == address_id, Address.user_id == current_user.user_id).first()
    if not addr:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")

    was_default = addr.is_default
    db.delete(addr)
    db.commit()

    # If deleted address was default, promote another address to default
    if was_default:
        next_addr = db.query(Address).filter(Address.user_id == current_user.user_id).first()
        if next_addr:
            next_addr.is_default = True
            db.commit()

    return {"message": "Address deleted successfully", "address_id": address_id}
