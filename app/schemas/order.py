from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from app.models.order import OrderStatus


# --- Esquemas de entrada ---

class OrderStatusUpdate(BaseModel):
    status: OrderStatus


# --- Esquemas de salida ---

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: float

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    user_id: int
    store_id: int
    total_amount: float
    status: OrderStatus
    items: List[OrderItemResponse]
    created_at: datetime

    class Config:
        from_attributes = True