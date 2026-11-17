from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class AddressBase(BaseModel):
    recipient_name: str
    phone: str
    house_building: Optional[str] = None
    street_address: str
    area_locality: Optional[str] = None
    city: str
    state: str
    pincode: str
    is_default: bool = False
    address_type: str = "HOME"

class AddressCreate(AddressBase):
    pass

class AddressUpdate(BaseModel):
    recipient_name: Optional[str] = None
    phone: Optional[str] = None
    house_building: Optional[str] = None
    street_address: Optional[str] = None
    area_locality: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    is_default: Optional[bool] = None
    address_type: Optional[str] = None

class AddressResponse(AddressBase):
    address_id: int
    user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class VendorProfileResponse(BaseModel):
    vendor_id: int
    user_id: Optional[int] = None
    full_name: str
    email: str
    phone: str
    avatar_url: Optional[str] = None
    business_name: str
    owner_name: str
    category: str
    description: Optional[str] = None
    business_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    tax_id: Optional[str] = None
    status: str
    commission_rate: float
    preferences: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

class VendorProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    business_name: Optional[str] = None
    description: Optional[str] = None
    business_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

class CustomerProfileResponse(BaseModel):
    user_id: int
    full_name: str
    email: str
    phone: Optional[str] = None
    role: str
    avatar_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    default_address: Optional[AddressResponse] = None
    addresses: List[AddressResponse] = []
    created_at: Optional[datetime] = None

class CustomerProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
