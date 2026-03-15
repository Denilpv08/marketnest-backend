from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.order import Order, OrderItem, OrderStatus
from app.models.cart import CartItem
from app.schemas.order import OrderStatusUpdate


def create_order_from_cart(db: Session, user_id: int) -> Order:
    cart_items = db.query(CartItem).filter(CartItem.user_id == user_id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="El carrito está vacío")

    store_ids = set(item.product.store_id for item in cart_items)
    if len(store_ids) > 1:
        raise HTTPException(
            status_code=400,
            detail="Solo puedes comprar productos de una tienda a la vez"
        )

    store_id = store_ids.pop()
    total = sum(item.product.price * item.quantity for item in cart_items)

    order = Order(user_id=user_id, store_id=store_id, total_amount=total)
    db.add(order)
    db.flush()

    for item in cart_items:
        if item.product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente para '{item.product.name}'. Disponible: {item.product.stock}"
            )
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.product.price,
        )
        item.product.stock -= item.quantity
        db.add(order_item)

    db.commit()
    db.refresh(order)

    db.query(CartItem).filter(CartItem.user_id == user_id).delete()
    db.commit()

    return order


def get_orders_by_user(db: Session, user_id: int):
    return db.query(Order).filter(Order.user_id == user_id).all()


def get_orders_by_store(db: Session, store_id: int):
    return db.query(Order).filter(Order.store_id == store_id).all()


def get_order_by_id(db: Session, order_id: int) -> Order:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return order


def update_order_status(db: Session, order_id: int, data: OrderStatusUpdate) -> Order:
    order = get_order_by_id(db, order_id)
    if order.status == OrderStatus.cancelled:
        raise HTTPException(
            status_code=400,
            detail="No se puede actualizar una orden cancelada"
        )
    order.status = data.status
    db.commit()
    db.refresh(order)
    return order