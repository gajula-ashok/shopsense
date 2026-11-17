from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database import get_db
from app.models.user import User
from app.utils.security import get_current_active_user
from app.schemas.profile import (
    VendorProfileResponse,
    VendorProfileUpdate,
    CustomerProfileResponse,
    CustomerProfileUpdate,
    AddressCreate,
    AddressUpdate,
    AddressResponse
)
from app.services import profile_service

router = APIRouter(prefix="/api", tags=["Profile & Address Management"])

# Vendor Profile
@router.get("/vendor/profile", response_model=VendorProfileResponse)
def get_vendor_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retrieve comprehensive profile of the authenticated vendor."""
    return profile_service.get_vendor_profile(db, current_user)

@router.put("/vendor/profile", response_model=VendorProfileResponse)
def update_vendor_profile(
    payload: VendorProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update personal, business, contact, address, and preferences for authenticated vendor."""
    return profile_service.update_vendor_profile(db, current_user, payload)

# Customer Profile
@router.get("/customer/profile", response_model=CustomerProfileResponse)
def get_customer_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retrieve profile, default address, and preferences for authenticated user/customer."""
    return profile_service.get_customer_profile(db, current_user)

@router.put("/customer/profile", response_model=CustomerProfileResponse)
def update_customer_profile(
    payload: CustomerProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update name, phone, avatar, or preferences for authenticated user/customer."""
    return profile_service.update_customer_profile(db, current_user, payload)

# Address Management
@router.get("/addresses", response_model=List[AddressResponse])
def list_addresses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all saved delivery addresses for the authenticated user."""
    return profile_service.list_user_addresses(db, current_user)

@router.post("/addresses", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
def create_address(
    payload: AddressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add a new delivery address for the authenticated user."""
    return profile_service.create_user_address(db, current_user, payload)

@router.put("/addresses/{address_id}", response_model=AddressResponse)
def update_address(
    address_id: int,
    payload: AddressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a specific delivery address."""
    return profile_service.update_user_address(db, current_user, address_id, payload)

@router.put("/addresses/{address_id}/default", response_model=AddressResponse)
def set_default_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Set an address as the default delivery address."""
    return profile_service.set_default_address(db, current_user, address_id)

@router.delete("/addresses/{address_id}")
def delete_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a saved address."""
    return profile_service.delete_user_address(db, current_user, address_id)
