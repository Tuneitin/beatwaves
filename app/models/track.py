from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class TrackStatus(str, enum.Enum):
    pending = "pending"
    published = "published"
    archived = "archived"


class GenreType(str, enum.Enum):
    afrobeats = "afrobeats"
    hiphop = "hiphop"
    dancehall = "dancehall"
    highlife = "highlife"
    gospel = "gospel"


class Track(Base):
    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True, index=True)
    artist_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    genre = Column(Enum(GenreType), default=GenreType.afrobeats)
    file_url = Column(String, nullable=True)
    artwork_url = Column(String, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    release_date = Column(DateTime, nullable=True)
    status = Column(Enum(TrackStatus), default=TrackStatus.pending)
    platforms = Column(JSON, nullable=True, default=list)
    total_streams = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    artist = relationship("User", back_populates="tracks")
    royalties = relationship("Royalty", back_populates="track")
    sales = relationship("Sale", back_populates="track")

    __table_args__ = (
        Index("idx_track_artist_id", "artist_id"),
        Index("idx_track_status", "status"),
        Index("idx_track_created_at", "created_at"),
    )

