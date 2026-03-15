from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.service import DurationUnit
from app.schemas.service_category import ServiceCategoryResponse


# --- Esquemas de entrada ---

class ServiceCreate(BaseModel):
    category_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float
    duration: int
    duration_unit: DurationUnit = DurationUnit.minutes
    image_url: Optional[str] = None


class ServiceUpdate(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    duration: Optional[int] = None
    duration_unit: Optional[DurationUnit] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None


# --- Esquemas de salida ---

class ServiceResponse(BaseModel):
    id: int
    store_id: int
    category_id: Optional[int]
    name: str
    description: Optional[str]
    price: float
    duration: int
    duration_unit: DurationUnit
    image_url: Optional[str]
    is_active: bool
    category: Optional[ServiceCategoryResponse]
    created_at: datetime

    class Config:
        from_attributes = True