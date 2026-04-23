from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.user import PlanType


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    artist_name: str
    location: Optional[str] = "Ghana"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    artist_name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    momo_number: Optional[str] = None
    momo_network: Optional[str] = None


class UserOut(BaseModel):
    id: int
    email: str
    artist_name: str
    bio: Optional[str]
    location: Optional[str]
    momo_number: Optional[str]
    momo_network: Optional[str]
    plan: PlanType
    avatar_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut
