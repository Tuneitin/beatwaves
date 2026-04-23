from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.royalty import Royalty, RoyaltyStatus
from app.schemas.payment import RoyaltyOut, RoyaltySummary

router = APIRouter(prefix="/royalties", tags=["Royalties"])


@router.get("/", response_model=List[RoyaltyOut])
def list_royalties(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Royalty).filter(Royalty.artist_id == current_user.id).order_by(Royalty.created_at.desc()).all()


@router.get("/summary", response_model=RoyaltySummary)
def royalty_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    paid = db.query(func.sum(Royalty.amount_ghs)).filter(
        Royalty.artist_id == current_user.id,
        Royalty.status == RoyaltyStatus.paid,
    ).scalar() or 0.0

    pending = db.query(func.sum(Royalty.amount_ghs)).filter(
        Royalty.artist_id == current_user.id,
        Royalty.status == RoyaltyStatus.pending,
    ).scalar() or 0.0

    lifetime = db.query(func.sum(Royalty.amount_ghs)).filter(
        Royalty.artist_id == current_user.id,
    ).scalar() or 0.0

    return RoyaltySummary(
        available_ghs=round(paid, 2),
        pending_ghs=round(pending, 2),
        lifetime_ghs=round(lifetime, 2),
    )
