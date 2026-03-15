from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.cart import CartItem
from app.models.product import Product


def get_cart(db: Session, user_id: int) -> dict:
    items = db.query(CartItem).filter(CartItem.user_id == user_id).all()
    total = sum(item.product.price * item.quantity for item in items)
    return {"items": items, "total": total}


def add_to_cart(db: Session, user_id: int, product_id: int, quantity: int) -> CartItem:
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_active == True
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if product.stock < quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Stock insuficiente. Disponible: {product.stock}"
        )

    existing = db.query(CartItem).filter(
        CartItem.user_id == user_id,
        CartItem.product_id == product_id
    ).first()

    if existing:
        existing.quantity += quantity
        db.commit()
        db.refresh(existing)
        return existing

    item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def remove_from_cart(db: Session, user_id: int, item_id: int):
    item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.user_id == user_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Ítem no encontrado en el carrito")
    db.delete(item)
    db.commit()


def update_cart_item(db: Session, user_id: int, item_id: int, quantity: int) -> CartItem:
    item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.user_id == user_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Ítem no encontrado en el carrito")
    if item.product.stock < quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Stock insuficiente. Disponible: {item.product.stock}"
        )
    item.quantity = quantity
    db.commit()
    db.refresh(item)
    return item


def clear_cart(db: Session, user_id: int):
    db.query(CartItem).filter(CartItem.user_id == user_id).delete()
    db.commit()