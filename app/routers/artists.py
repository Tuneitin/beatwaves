from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.track import Track
from app.schemas.user import UserOut
from app.schemas.track import TrackOut
from app.core.pagination import PaginatedResponse

router = APIRouter(prefix="/artists", tags=["Artists"])


class ArtistProfileOut(UserOut):
    track_count: int
    total_streams: int


@router.get("/{artist_id}")
def get_artist_profile(
    artist_id: int,
    db: Session = Depends(get_db),
):
    """Get public artist profile with stats."""
    artist = db.query(User).filter(User.id == artist_id).first()
    if not artist:
        raise HTTPException(404, "Artist not found")

    track_count = db.query(func.count(Track.id)).filter(Track.artist_id == artist_id).scalar()
    total_streams = db.query(func.sum(Track.total_streams)).filter(Track.artist_id == artist_id).scalar() or 0

    profile = ArtistProfileOut(
        **UserOut.from_orm(artist).model_dump(),
        track_count=track_count,
        total_streams=total_streams,
    )
    return profile


@router.get("/{artist_id}/tracks")
def get_artist_tracks(
    artist_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get artist's published tracks."""
    artist = db.query(User).filter(User.id == artist_id).first()
    if not artist:
        raise HTTPException(404, "Artist not found")

    total = db.query(func.count(Track.id)).filter(
        Track.artist_id == artist_id,
        Track.status == "published"
    ).scalar()

    offset = (page - 1) * page_size
    tracks = db.query(Track).filter(
        Track.artist_id == artist_id,
        Track.status == "published"
    ).offset(offset).limit(page_size).all()

    return PaginatedResponse.create(tracks, total, page, page_size)


@router.get("/search")
def search_artists(
    q: str = Query(..., min_length=1, max_length=100, description="Search query"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Search for artists by name."""
    total = db.query(func.count(User.id)).filter(
        User.artist_name.ilike(f"%{q}%")
    ).scalar()

    offset = (page - 1) * page_size
    artists = db.query(User).filter(
        User.artist_name.ilike(f"%{q}%")
    ).offset(offset).limit(page_size).all()

    return PaginatedResponse.create(
        [UserOut.from_orm(a) for a in artists],
        total,
        page,
        page_size,
    )
