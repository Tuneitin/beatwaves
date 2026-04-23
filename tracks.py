from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.track import Track, TrackStatus, GenreType
from app.schemas.track import TrackOut, TrackUpdate
from app.services.file_upload import save_track_file, save_artwork_file

router = APIRouter(prefix="/tracks", tags=["Tracks"])


@router.get("/", response_model=List[TrackOut])
def list_my_tracks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Track).filter(Track.artist_id == current_user.id).all()


@router.post("/", response_model=TrackOut, status_code=201)
async def upload_track(
    title: str = Form(...),
    genre: GenreType = Form(GenreType.afrobeats),
    release_date: Optional[str] = Form(None),
    platforms: Optional[str] = Form(""),  # comma-separated
    track_file: UploadFile = File(...),
    artwork_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file_url = await save_track_file(track_file, current_user.id)
    artwork_url = None
    if artwork_file and artwork_file.filename:
        artwork_url = await save_artwork_file(artwork_file, current_user.id)

    platform_list = [p.strip() for p in platforms.split(",") if p.strip()] if platforms else []
    parsed_date = datetime.fromisoformat(release_date) if release_date else None

    track = Track(
        artist_id=current_user.id,
        title=title,
        genre=genre,
        file_url=file_url,
        artwork_url=artwork_url,
        release_date=parsed_date,
        platforms=platform_list,
        status=TrackStatus.pending,
    )
    db.add(track)
    db.commit()
    db.refresh(track)
    return track


@router.get("/{track_id}", response_model=TrackOut)
def get_track(
    track_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    track = db.query(Track).filter(Track.id == track_id, Track.artist_id == current_user.id).first()
    if not track:
        raise HTTPException(404, "Track not found")
    return track


@router.patch("/{track_id}", response_model=TrackOut)
def update_track(
    track_id: int,
    data: TrackUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    track = db.query(Track).filter(Track.id == track_id, Track.artist_id == current_user.id).first()
    if not track:
        raise HTTPException(404, "Track not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(track, field, value)
    db.commit()
    db.refresh(track)
    return track


@router.delete("/{track_id}", status_code=204)
def delete_track(
    track_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    track = db.query(Track).filter(Track.id == track_id, Track.artist_id == current_user.id).first()
    if not track:
        raise HTTPException(404, "Track not found")
    db.delete(track)
    db.commit()


@router.patch("/{track_id}/artwork")
async def update_artwork(
    track_id: int,
    artwork_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    track = db.query(Track).filter(Track.id == track_id, Track.artist_id == current_user.id).first()
    if not track:
        raise HTTPException(404, "Track not found")
    track.artwork_url = await save_artwork_file(artwork_file, current_user.id)
    db.commit()
    return {"artwork_url": track.artwork_url}
