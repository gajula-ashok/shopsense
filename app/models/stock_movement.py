from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
import enum
from app.database import Base

class MovementType(str, enum.Enum):
    STOCK_IN = "STOCK_IN"
    STOCK_OUT = "STOCK_OUT"
    ADJUSTMENT = "ADJUSTMENT"
    SALE = "SALE"
    RETURN = "RETURN"

class StockMovement(Base):
    __tablename__ = "stock_movements"

    movement_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)  # positive for addition, negative for reduction
    movement_type = Column(String(30), default="ADJUSTMENT", nullable=False)
    reference = Column(String(100), nullable=True)  # e.g., Order #, PO #, Restock
    warehouse = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    product = relationship("Product")

    def __repr__(self):
        return f"<StockMovement id={self.movement_id} product_id={self.product_id} qty={self.quantity} type={self.movement_type}>"
