from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from app.models.transaction import TransactionType, TransactionStatus
from app.models.royalty import RoyaltyStatus

VALID_NETWORKS = {"mtn", "vodafone", "airteltigo"}


class MoMoPayRequest(BaseModel):
    amount_ghs: float = Field(..., gt=0, description="Amount must be greater than 0")
    momo_number: str = Field(..., min_length=10, max_length=20, description="Valid MoMo phone number")
    momo_network: str = Field(..., description="mtn, vodafone, or airteltigo")
    description: Optional[str] = Field(None, max_length=255)
    transaction_type: TransactionType = TransactionType.subscription

    @field_validator("amount_ghs")
    @classmethod
    def validate_amount(cls, v):
        if v > 10000:
            raise ValueError("Amount cannot exceed 10,000 GHS")
        return v

    @field_validator("momo_network")
    @classmethod
    def validate_network(cls, v):
        if v.lower() not in VALID_NETWORKS:
            raise ValueError(f"Network must be one of: {', '.join(VALID_NETWORKS)}")
        return v.lower()

    @field_validator("momo_number")
    @classmethod
    def validate_momo_number(cls, v):
        if not v.replace("+", "").replace(" ", "").isdigit():
            raise ValueError("MoMo number must contain only digits, + and spaces")
        return v


class WithdrawRequest(BaseModel):
    amount_ghs: float = Field(..., gt=0, description="Amount must be greater than 0")
    momo_number: str = Field(..., min_length=10, max_length=20)
    momo_network: str = Field(..., description="mtn, vodafone, or airteltigo")

    @field_validator("amount_ghs")
    @classmethod
    def validate_amount(cls, v):
        if v > 10000:
            raise ValueError("Amount cannot exceed 10,000 GHS")
        return v

    @field_validator("momo_network")
    @classmethod
    def validate_network(cls, v):
        if v.lower() not in VALID_NETWORKS:
            raise ValueError(f"Network must be one of: {', '.join(VALID_NETWORKS)}")
        return v.lower()

    @field_validator("momo_number")
    @classmethod
    def validate_momo_number(cls, v):
        if not v.replace("+", "").replace(" ", "").isdigit():
            raise ValueError("MoMo number must contain only digits, + and spaces")
        return v


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
