from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class SaleType(str, enum.Enum):
    digital_download = "digital_download"
    exclusive_stems = "exclusive_stems"
    limited_bundle = "limited_bundle"
    pay_what_you_want = "pay_what_you_want"


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)
    sale_type = Column(Enum(SaleType), default=SaleType.digital_download)
    price_ghs = Column(Float, nullable=False)
    copies_limit = Column(Integer, nullable=True)   # null = unlimited
    copies_sold = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    slug = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    seller = relationship("User", back_populates="sales")
    track = relationship("Track", back_populates="sales")
    purchases = relationship("Purchase", back_populates="sale")


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    buyer_email = Column(String, nullable=False)
    buyer_name = Column(String, nullable=True)
    amount_paid_ghs = Column(Float, nullable=False)
    momo_number = Column(String, nullable=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=True)
    download_token = Column(String, unique=True, nullable=True)
    downloaded = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sale = relationship("Sale", back_populates="purchases")
