from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
import stripe

from app.database import get_db
from app.schemas.payment import PaymentCreate, CheckoutResponse, PaymentResponse
from app.services import payment_service
from app.middleware.auth import get_current_user
from app.models.user import User
from app.config import settings

router = APIRouter(prefix="/api/payments", tags=["Pagos"])


@router.post("/checkout", response_model=CheckoutResponse)
def checkout(
    data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crea un PaymentIntent en Stripe y devuelve el client_secret."""
    return payment_service.create_payment_intent(db, data.order_id, current_user.id)


@router.get("/order/{order_id}", response_model=PaymentResponse)
def get_payment(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene el pago asociado a una orden."""
    return payment_service.get_payment_by_order(db, order_id)


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Webhook de Stripe — Stripe llama aquí cuando el pago cambia de estado.
    No requiere autenticación JWT, usa firma de Stripe.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Webhook inválido")

    if event["type"] == "payment_intent.succeeded":
        stripe_payment_id = event["data"]["object"]["id"]
        payment_service.confirm_payment(db, stripe_payment_id)

    elif event["type"] == "payment_intent.payment_failed":
        stripe_payment_id = event["data"]["object"]["id"]
        payment_service.fail_payment(db, stripe_payment_id)

    return {"status": "ok"}