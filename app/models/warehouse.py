from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class Warehouse(Base):
    __tablename__ = "warehouses"

    warehouse_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    warehouse_name = Column(String(120), nullable=False, unique=True, index=True)
    location = Column(String(200), nullable=False)
    capacity = Column(Integer, default=10000, nullable=False)
    contact_phone = Column(String(30), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<Warehouse id={self.warehouse_id} name={self.warehouse_name} location={self.location}>"
