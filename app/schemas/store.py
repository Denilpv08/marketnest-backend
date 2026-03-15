from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, Dict, Any
from app.models.store import StoreStatus, StoreType, BusinessType


# --- Schema para horarios ---

class DaySchedule(BaseModel):
    open: str    # Formato "08:00"
    close: str   # Formato "18:00"


# --- Esquemas de entrada ---

class StoreCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    store_type: Optional[StoreType] = None
    custom_store_type: Optional[str] = None
    business_type: BusinessType = BusinessType.products
    tax_id: Optional[str] = None
    phone: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    city: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    opening_hours: Optional[Dict[str, Optional[DaySchedule]]] = None
    allows_appointments: bool = False


class StoreUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    store_type: Optional[StoreType] = None
    custom_store_type: Optional[str] = None
    business_type: Optional[BusinessType] = None
    tax_id: Optional[str] = None
    phone: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    city: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    opening_hours: Optional[Dict[str, Optional[DaySchedule]]] = None
    allows_appointments: Optional[bool] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None


class StoreStatusUpdate(BaseModel):
    status: StoreStatus


# --- Esquemas de salida ---

class StoreResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    owner_id: int
    status: StoreStatus
    store_type: Optional[StoreType]
    custom_store_type: Optional[str]
    business_type: BusinessType
    tax_id: Optional[str]
    phone: Optional[str]
    contact_email: Optional[str]
    city: Optional[str]
    address: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    opening_hours: Optional[Dict[str, Any]]
    allows_appointments: bool
    logo_url: Optional[str]
    primary_color: str
    secondary_color: str
    banner_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True