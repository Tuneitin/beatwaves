from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class TransactionType(str, enum.Enum):
    subscription = "subscription"
    distribution_fee = "distribution_fee"
    withdrawal = "withdrawal"
    fan_sale = "fan_sale"


class TransactionStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"
    refunded = "refunded"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    amount_ghs = Column(Float, nullable=False)
    momo_number = Column(String, nullable=True)
    momo_network = Column(String, nullable=True)
    hubtel_reference = Column(String, nullable=True, unique=True)
    external_reference = Column(String, nullable=True)
    description = Column(String, nullable=True)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.pending)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="transactions")
