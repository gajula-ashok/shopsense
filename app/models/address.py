from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class Address(Base):
    __tablename__ = "addresses"

    address_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    recipient_name = Column(String(120), nullable=False)
    phone = Column(String(30), nullable=False)
    house_building = Column(String(100), nullable=True)
    street_address = Column(String(255), nullable=False)
    area_locality = Column(String(150), nullable=True)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    pincode = Column(String(20), nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    address_type = Column(String(20), default="HOME", nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="addresses")

    def __repr__(self):
        return f"<Address id={self.address_id} user_id={self.user_id} city={self.city} default={self.is_default}>"
