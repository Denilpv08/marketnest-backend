from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.store import StoreStatus


# --- Esquemas de entrada ---

class StoreCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None


class StoreUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
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
    logo_url: Optional[str]
    primary_color: str
    secondary_color: str
    banner_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True