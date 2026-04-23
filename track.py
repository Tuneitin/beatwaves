from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.track import TrackStatus, GenreType


class TrackCreate(BaseModel):
    title: str
    genre: GenreType = GenreType.afrobeats
    release_date: Optional[datetime] = None
    platforms: Optional[List[str]] = []


class TrackUpdate(BaseModel):
    title: Optional[str] = None
    genre: Optional[GenreType] = None
    release_date: Optional[datetime] = None
    platforms: Optional[List[str]] = None


class TrackOut(BaseModel):
    id: int
    artist_id: int
    title: str
    genre: GenreType
    file_url: Optional[str]
    artwork_url: Optional[str]
    duration_seconds: Optional[int]
    release_date: Optional[datetime]
    status: TrackStatus
    platforms: Optional[List[str]]
    total_streams: int
    created_at: datetime

    class Config:
        from_attributes = True
