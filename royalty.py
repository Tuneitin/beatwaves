from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class RoyaltyStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    withdrawn = "withdrawn"


class Royalty(Base):
    __tablename__ = "royalties"

    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)
    artist_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    platform = Column(String, nullable=False)
    streams = Column(Integer, default=0)
    amount_ghs = Column(Float, default=0.0)   # Ghana Cedis
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)
    status = Column(Enum(RoyaltyStatus), default=RoyaltyStatus.pending)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    track = relationship("Track", back_populates="royalties")
