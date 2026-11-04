from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.models.vendor import VendorStatus

class VendorCreate(BaseModel):
    business_name: str = Field(..., min_length=2, max_length=150)
    owner_name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=30)
    category: str = Field(..., min_length=2, max_length=80)
    commission_rate: Optional[Decimal] = Field(default=Decimal("10.00"), ge=0, le=100)
    status: Optional[VendorStatus] = VendorStatus.ACTIVE
    user_id: Optional[int] = None
    business_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    tax_id: Optional[str] = None

class VendorUpdate(BaseModel):
    business_name: Optional[str] = Field(None, min_length=2, max_length=150)
    owner_name: Optional[str] = Field(None, min_length=2, max_length=120)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=10, max_length=30)
    category: Optional[str] = Field(None, min_length=2, max_length=80)
    commission_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    status: Optional[VendorStatus] = None
    business_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    tax_id: Optional[str] = None
    application_status: Optional[str] = None
    review_notes: Optional[str] = None

class VendorApplicationReview(BaseModel):
    action: str = Field(..., description="APPROVE, REQUEST_INFO, or REJECT")
    notes: Optional[str] = Field(None, description="Admin review commentary or explanation")

class VendorResponse(BaseModel):
    vendor_id: int
    business_name: str
    owner_name: str
    email: str
    phone: str
    category: str
    commission_rate: Decimal
    status: VendorStatus
    created_at: datetime
    user_id: Optional[int] = None
    business_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    tax_id: Optional[str] = None
    review_notes: Optional[str] = None
    application_status: Optional[str] = "APPROVED"

    model_config = {"from_attributes": True}
