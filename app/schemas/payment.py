from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.transaction import TransactionType, TransactionStatus
from app.models.royalty import RoyaltyStatus


class MoMoPayRequest(BaseModel):
    amount_ghs: float
    momo_number: str
    momo_network: str          # mtn, vodafone, airteltigo
    description: Optional[str] = None
    transaction_type: TransactionType = TransactionType.subscription


class WithdrawRequest(BaseModel):
    amount_ghs: float
    momo_number: str
    momo_network: str


class TransactionOut(BaseModel):
    id: int
    type: TransactionType
    amount_ghs: float
    momo_number: Optional[str]
    momo_network: Optional[str]
    description: Optional[str]
    status: TransactionStatus
    created_at: datetime

    class Config:
        from_attributes = True


class RoyaltyOut(BaseModel):
    id: int
    track_id: int
    platform: str
    streams: int
    amount_ghs: float
    status: RoyaltyStatus
    created_at: datetime

    class Config:
        from_attributes = True


class RoyaltySummary(BaseModel):
    available_ghs: float
    pending_ghs: float
    lifetime_ghs: float


class SaleCreate(BaseModel):
    track_id: int
    sale_type: str = "digital_download"
    price_ghs: float
    copies_limit: Optional[int] = None


class SaleOut(BaseModel):
    id: int
    track_id: int
    sale_type: str
    price_ghs: float
    copies_limit: Optional[int]
    copies_sold: int
    is_active: bool
    slug: str
    created_at: datetime

    class Config:
        from_attributes = True


class PurchaseRequest(BaseModel):
    buyer_email: str
    buyer_name: Optional[str] = None
    momo_number: str
    amount_paid_ghs: float


class HubtelCallbackPayload(BaseModel):
    ClientReference: Optional[str] = None
    Status: Optional[str] = None
    Data: Optional[dict] = None


class CallbackSimulationRequest(BaseModel):
    external_reference: str
    status: str
