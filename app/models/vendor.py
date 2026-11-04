from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, Enum as SQLEnum, func
from sqlalchemy.orm import relationship
import enum
from app.database import Base

class VendorStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"

class Vendor(Base):
    __tablename__ = "vendors"

    vendor_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    business_name = Column(String(150), nullable=False)
    owner_name = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    phone = Column(String(30), nullable=False)
    category = Column(String(80), nullable=False, index=True)
    commission_rate = Column(Numeric(5, 2), default=10.00, nullable=False)
    status = Column(SQLEnum(VendorStatus), default=VendorStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True, unique=True)

    # Vendor Application Management fields
    business_address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    pincode = Column(String(20), nullable=True)
    tax_id = Column(String(50), nullable=True)  # GSTIN / PAN
    review_notes = Column(Text, nullable=True)
    application_status = Column(String(50), default="APPROVED", nullable=True)  # PENDING, APPROVED, MORE_INFO_NEEDED, REJECTED

    user = relationship("User", back_populates="vendor")
    products = relationship("Product", back_populates="vendor", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="vendor")

    def __repr__(self):
        return f"<Vendor id={self.vendor_id} business={self.business_name} status={self.status} app_status={self.application_status}>"
