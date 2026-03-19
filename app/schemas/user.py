from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from app.models.user import UserRole, IdentityType, UserStatus


# --- Esquemas de entrada ---

class UserCreate(BaseModel):
    name: str
    last_name: Optional[str] = None
    email: EmailStr
    password: str
    role: UserRole = UserRole.customer
    identity_type: Optional[IdentityType] = None
    identity_number: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    identity_type: Optional[IdentityType] = None
    identity_number: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    photo_url: Optional[str] = None


class UserStatusUpdate(BaseModel):
    status: UserStatus


# --- Esquemas de salida ---

class UserResponse(BaseModel):
    id: int
    name: str
    last_name: Optional[str]
    email: str
    role: UserRole
    status: UserStatus
    identity_type: Optional[IdentityType]
    identity_number: Optional[str]
    city: Optional[str]
    address: Optional[str]
    photo_url: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse