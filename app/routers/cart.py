from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartResponse
from app.services import cart_service
from app.middleware.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/cart", tags=["Carrito"])


@router.get("/", response_model=CartResponse)
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene el carrito del usuario autenticado."""
    return cart_service.get_cart(db, current_user.id)


@router.post("/", status_code=201)
def add_item(
    data: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Agrega un producto al carrito."""
    return cart_service.add_to_cart(db, current_user.id, data.product_id, data.quantity)


@router.put("/{item_id}")
def update_item(
    item_id: int,
    data: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualiza la cantidad de un ítem del carrito."""
    return cart_service.update_cart_item(db, current_user.id, item_id, data.quantity)


@router.delete("/{item_id}", status_code=204)
def remove_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Elimina un ítem del carrito."""
    cart_service.remove_from_cart(db, current_user.id, item_id)


@router.delete("/", status_code=204)
def clear_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Vacía todo el carrito."""
    cart_service.clear_cart(db, current_user.id)