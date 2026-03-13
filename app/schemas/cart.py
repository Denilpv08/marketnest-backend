from pydantic import BaseModel
from datetime import datetime
from typing import List
from app.schemas.product import ProductResponse


# --- Esquemas de entrada ---

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = 1


class CartItemUpdate(BaseModel):
    quantity: int


# --- Esquemas de salida ---

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: ProductResponse
    created_at: datetime

    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    items: List[CartItemResponse]
    total: float