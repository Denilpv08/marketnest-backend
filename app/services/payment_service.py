import stripe
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.config import settings
from app.models.payment import Payment, PaymentStatus
from app.models.order import Order, OrderStatus

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_payment_intent(db: Session, order_id: int, user_id: int) -> dict:
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user_id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    if order.status != OrderStatus.pending:
        raise HTTPException(status_code=400, detail="Esta orden ya fue procesada")

    existing_payment = db.query(Payment).filter(
        Payment.order_id == order_id
    ).first()
    if existing_payment:
        raise HTTPException(status_code=400, detail="Esta orden ya tiene un pago iniciado")

    intent = stripe.PaymentIntent.create(
        amount=int(order.total_amount * 100),
        currency="usd",
        metadata={"order_id": order_id, "user_id": user_id}
    )

    payment = Payment(
        order_id=order_id,
        stripe_payment_id=intent.id,
        amount=order.total_amount,
        status=PaymentStatus.pending,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    return {"client_secret": intent.client_secret, "payment_id": payment.id}


def confirm_payment(db: Session, stripe_payment_id: str):
    """Llamado desde el webhook de Stripe cuando el pago es confirmado."""
    payment = db.query(Payment).filter(
        Payment.stripe_payment_id == stripe_payment_id
    ).first()
    if not payment:
        return

    payment.status = PaymentStatus.succeeded
    payment.order.status = OrderStatus.paid
    db.commit()


def fail_payment(db: Session, stripe_payment_id: str):
    """Llamado desde el webhook de Stripe cuando el pago falla."""
    payment = db.query(Payment).filter(
        Payment.stripe_payment_id == stripe_payment_id
    ).first()
    if not payment:
        return

    payment.status = PaymentStatus.failed
    db.commit()


def get_payment_by_order(db: Session, order_id: int) -> Payment:
    payment = db.query(Payment).filter(Payment.order_id == order_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    return payment