import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, PlanType
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.models.royalty import Royalty, RoyaltyStatus
from app.schemas.payment import MoMoPayRequest, WithdrawRequest, TransactionOut
from app.services import momo

router = APIRouter(prefix="/payments", tags=["Payments"])

PLAN_PRICES = {
    PlanType.starter: 0,
    PlanType.pro: 99,
    PlanType.label: 350,
}


@router.post("/subscribe/{plan}", response_model=TransactionOut)
async def subscribe(
    plan: PlanType,
    momo_number: str,
    momo_network: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    price = PLAN_PRICES[plan]
    if price == 0:
        current_user.plan = plan
        db.commit()
        raise HTTPException(200, "Switched to free Starter plan")

    ref = str(uuid.uuid4())
    tx = Transaction(
        user_id=current_user.id,
        type=TransactionType.subscription,
        amount_ghs=price,
        momo_number=momo_number,
        momo_network=momo_network,
        description=f"BeatWave {plan.value.title()} plan subscription",
        external_reference=ref,
        status=TransactionStatus.pending,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)

    result = await momo.request_payment(
        amount=price,
        momo_number=momo_number,
        network=momo_network,
        description=f"BeatWave {plan.value.title()} plan",
        reference=ref,
    )

    if result.get("status") == "success":
        tx.status = TransactionStatus.completed
        tx.hubtel_reference = result["data"].get("transactionId")
        current_user.plan = plan
        db.commit()
    else:
        tx.status = TransactionStatus.failed
        db.commit()
        raise HTTPException(400, "Payment failed. Please try again.")

    db.refresh(tx)
    return tx


@router.post("/withdraw", response_model=TransactionOut)
async def withdraw_royalties(
    data: WithdrawRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    available = db.query(func.sum(Royalty.amount_ghs)).filter(
        Royalty.artist_id == current_user.id,
        Royalty.status == RoyaltyStatus.paid,
    ).scalar() or 0.0

    if data.amount_ghs > available:
        raise HTTPException(400, f"Insufficient balance. Available: GH₵{available:.2f}")

    ref = str(uuid.uuid4())
    tx = Transaction(
        user_id=current_user.id,
        type=TransactionType.withdrawal,
        amount_ghs=data.amount_ghs,
        momo_number=data.momo_number,
        momo_network=data.momo_network,
        description="Royalty withdrawal",
        external_reference=ref,
        status=TransactionStatus.pending,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)

    result = await momo.request_withdrawal(
        amount=data.amount_ghs,
        momo_number=data.momo_number,
        network=data.momo_network,
        reference=ref,
    )

    if result.get("status") == "success":
        # Mark royalties as withdrawn up to the amount
        royalties = db.query(Royalty).filter(
            Royalty.artist_id == current_user.id,
            Royalty.status == RoyaltyStatus.paid,
        ).all()
        remaining = data.amount_ghs
        for r in royalties:
            if remaining <= 0:
                break
            if r.amount_ghs <= remaining:
                remaining -= r.amount_ghs
                r.status = RoyaltyStatus.withdrawn
            else:
                r.amount_ghs -= remaining
                remaining = 0

        tx.status = TransactionStatus.completed
        tx.hubtel_reference = result["data"].get("transactionId")
        db.commit()
    else:
        tx.status = TransactionStatus.failed
        db.commit()
        raise HTTPException(400, "Withdrawal failed. Please try again.")

    db.refresh(tx)
    return tx


@router.get("/transactions", response_model=List[TransactionOut])
def list_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).order_by(Transaction.created_at.desc()).limit(50).all()


@router.post("/callback")
async def hubtel_callback(request: Request, db: Session = Depends(get_db)):
    """Hubtel webhook — called when payment status changes."""
    body = await request.json()
    ref = body.get("ClientReference") or body.get("Data", {}).get("ClientReference")
    if not ref:
        return {"status": "ignored"}

    tx = db.query(Transaction).filter(Transaction.external_reference == ref).first()
    if not tx:
        return {"status": "not_found"}

    hubtel_status = body.get("Status", "").lower()
    if hubtel_status in ("success", "successful"):
        tx.status = TransactionStatus.completed
    elif hubtel_status in ("failed", "error"):
        tx.status = TransactionStatus.failed

    db.commit()
    return {"status": "ok"}
