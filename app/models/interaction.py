from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class ProductInteraction(Base):
    __tablename__ = "product_interactions"

    interaction_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False, index=True)
    interaction_score = Column(Float, default=1.0, nullable=False)  # Rating, purchase weight, or view score (1.0 - 5.0)
    interaction_type = Column(String(50), default="PURCHASE", nullable=False) # PURCHASE, RATING, VIEW, WISHLIST
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    user = relationship("User")
    product = relationship("Product")

    __table_args__ = (
        UniqueConstraint('user_id', 'product_id', 'interaction_type', name='uq_user_product_interaction'),
    )

    def __repr__(self):
        return f"<ProductInteraction user={self.user_id} product={self.product_id} score={self.interaction_score}>"
