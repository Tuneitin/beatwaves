from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class PlanType(str, enum.Enum):
    starter = "starter"
    pro = "pro"
    label = "label"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    artist_name = Column(String, nullable=False)
    bio = Column(String, nullable=True)
    location = Column(String, nullable=True)
    momo_number = Column(String, nullable=True)
    momo_network = Column(String, nullable=True)
    plan = Column(Enum(PlanType), default=PlanType.starter)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tracks = relationship("Track", back_populates="artist")
    transactions = relationship("Transaction", back_populates="user")
    sales = relationship("Sale", back_populates="seller")
    royalties = relationship("Royalty", back_populates="artist")
