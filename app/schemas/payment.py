from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.payment import PaymentStatus


# --- Esquemas de entrada ---

class PaymentCreate(BaseModel):
    order_id: int


# --- Esquemas de salida ---

class PaymentResponse(BaseModel):
    id: int
    order_id: int
    stripe_payment_id: Optional[str]
    amount: float
    status: PaymentStatus
    created_at: datetime

    class Config:
        from_attributes = True


class CheckoutResponse(BaseModel):
    client_secret: str
    payment_id: int