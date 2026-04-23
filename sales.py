import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.sale import Sale, Purchase, SaleType
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.schemas.payment import SaleCreate, SaleOut, PurchaseRequest
from app.services import momo

router = APIRouter(prefix="/sales", tags=["Fan Sales"])


def _make_slug(artist_name: str, title: str) -> str:
    base = f"{artist_name}-{title}".lower().replace(" ", "-")
    return f"{base}-{uuid.uuid4().hex[:6]}"


@router.get("/", response_model=List[SaleOut])
def list_my_sales(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Sale).filter(Sale.seller_id == current_user.id).all()


@router.post("/", response_model=SaleOut, status_code=201)
def create_sale(
    data: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models.track import Track
    track = db.query(Track).filter(Track.id == data.track_id, Track.artist_id == current_user.id).first()
    if not track:
        raise HTTPException(404, "Track not found")

    slug = _make_slug(current_user.artist_name, track.title)
    sale = Sale(
        seller_id=current_user.id,
        track_id=data.track_id,
        sale_type=data.sale_type,
        price_ghs=data.price_ghs,
        copies_limit=data.copies_limit,
        slug=slug,
    )
    db.add(sale)
    db.commit()
    db.refresh(sale)
    return sale


@router.get("/store/{artist_slug}")
def get_artist_store(artist_slug: str, db: Session = Depends(get_db)):
    """Public storefront for a given artist."""
    user = db.query(User).filter(
        User.artist_name.ilike(artist_slug.replace("-", " "))
    ).first()
    if not user:
        raise HTTPException(404, "Artist not found")

    listings = db.query(Sale).filter(Sale.seller_id == user.id, Sale.is_active == True).all()
    return {
        "artist": {"name": user.artist_name, "bio": user.bio, "avatar": user.avatar_url},
        "listings": [SaleOut.from_orm(s) for s in listings],
    }


@router.post("/{slug}/purchase")
async def purchase(
    slug: str,
    data: PurchaseRequest,
    db: Session = Depends(get_db),
):
    sale = db.query(Sale).filter(Sale.slug == slug, Sale.is_active == True).first()
    if not sale:
        raise HTTPException(404, "Listing not found or no longer active")

    if sale.copies_limit and sale.copies_sold >= sale.copies_limit:
        raise HTTPException(400, "Sold out!")

    if data.amount_paid_ghs < sale.price_ghs:
        raise HTTPException(400, f"Minimum price is GH₵{sale.price_ghs}")

    ref = str(uuid.uuid4())
    tx = Transaction(
        user_id=sale.seller_id,
        type=TransactionType.fan_sale,
        amount_ghs=data.amount_paid_ghs,
        momo_number=data.momo_number,
        description=f"Fan purchase — {sale.track.title}",
        external_reference=ref,
        status=TransactionStatus.pending,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)

    result = await momo.request_payment(
        amount=data.amount_paid_ghs,
        momo_number=data.momo_number,
        network="mtn",
        description=f"Purchase: {sale.track.title}",
        reference=ref,
    )

    if result.get("status") == "success":
        tx.status = TransactionStatus.completed
        download_token = uuid.uuid4().hex
        purchase = Purchase(
            sale_id=sale.id,
            buyer_email=data.buyer_email,
            buyer_name=data.buyer_name,
            amount_paid_ghs=data.amount_paid_ghs,
            momo_number=data.momo_number,
            transaction_id=tx.id,
            download_token=download_token,
        )
        db.add(purchase)
        sale.copies_sold += 1
        db.commit()
        return {
            "status": "success",
            "download_token": download_token,
            "message": "Payment successful! Use the download token to access your file.",
        }
    else:
        tx.status = TransactionStatus.failed
        db.commit()
        raise HTTPException(400, "Payment failed.")


@router.get("/download/{token}")
def download_track(token: str, db: Session = Depends(get_db)):
    purchase = db.query(Purchase).filter(Purchase.download_token == token).first()
    if not purchase:
        raise HTTPException(404, "Invalid download token")
    if purchase.downloaded:
        raise HTTPException(410, "This download link has already been used")

    purchase.downloaded = True
    db.commit()
    return {"download_url": purchase.sale.track.file_url, "title": purchase.sale.track.title}
