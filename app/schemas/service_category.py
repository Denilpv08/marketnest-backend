from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# --- Esquemas de entrada ---

class ServiceCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ServiceCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


# --- Esquemas de salida ---

class ServiceCategoryResponse(BaseModel):
    id: int
    store_id: int
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True