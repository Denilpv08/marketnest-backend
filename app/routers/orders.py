from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.order import OrderResponse, OrderStatusUpdate
from app.services import order_service
from app.middleware.auth import get_current_user, require_admin
from app.models.user import User

router = APIRouter(prefix="/api/orders", tags=["Órdenes"])


@router.post("/", response_model=OrderResponse, status_code=201)
def create_order(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crea una orden a partir del carrito actual."""
    return order_service.create_order_from_cart(db, current_user.id)


@router.get("/my", response_model=List[OrderResponse])
def my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Historial de órdenes del usuario autenticado."""
    return order_service.get_orders_by_user(db, current_user.id)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene una orden por su ID."""
    order = order_service.get_order_by_id(db, order_id)
    if order.user_id != current_user.id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="No puedes ver esta orden")
    return order


@router.get("/store/{store_id}", response_model=List[OrderResponse])
def store_orders(
    store_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Órdenes recibidas por la tienda (solo admins)."""
    return order_service.get_orders_by_store(db, store_id)


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Actualiza el estado de una orden (solo admins)."""
    return order_service.update_order_status(db, order_id, data)