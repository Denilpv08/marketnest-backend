from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.order import Order, OrderStatus
from app.models.product import Product
from app.models.store import Store, StoreStatus
from app.models.user import User


def get_store_dashboard(db: Session, store_id: int) -> dict:
    """Estadísticas de ventas para el admin de una tienda."""

    total_sales = db.query(func.sum(Order.total_amount)).filter(
        Order.store_id == store_id,
        Order.status == OrderStatus.paid
    ).scalar() or 0

    total_orders = db.query(func.count(Order.id)).filter(
        Order.store_id == store_id
    ).scalar() or 0

    paid_orders = db.query(func.count(Order.id)).filter(
        Order.store_id == store_id,
        Order.status == OrderStatus.paid
    ).scalar() or 0

    total_products = db.query(func.count(Product.id)).filter(
        Product.store_id == store_id,
        Product.is_active == True
    ).scalar() or 0

    low_stock_products = db.query(Product).filter(
        Product.store_id == store_id,
        Product.stock <= 5,
        Product.is_active == True
    ).all()

    out_of_stock = db.query(Product).filter(
        Product.store_id == store_id,
        Product.stock == 0,
        Product.is_active == True
    ).all()

    return {
        "total_sales": round(total_sales, 2),
        "total_orders": total_orders,
        "paid_orders": paid_orders,
        "total_products": total_products,
        "low_stock_products": low_stock_products,
        "out_of_stock_products": out_of_stock,
    }


def get_superadmin_dashboard(db: Session) -> dict:
    """Estadísticas globales del sistema para el superadmin."""

    total_stores = db.query(func.count(Store.id)).scalar() or 0

    active_stores = db.query(func.count(Store.id)).filter(
        Store.status == StoreStatus.active
    ).scalar() or 0

    pending_stores = db.query(func.count(Store.id)).filter(
        Store.status == StoreStatus.pending
    ).scalar() or 0

    suspended_stores = db.query(func.count(Store.id)).filter(
        Store.status == StoreStatus.suspended
    ).scalar() or 0

    total_users = db.query(func.count(User.id)).scalar() or 0

    total_revenue = db.query(func.sum(Order.total_amount)).filter(
        Order.status == OrderStatus.paid
    ).scalar() or 0

    total_orders = db.query(func.count(Order.id)).filter(
        Order.status == OrderStatus.paid
    ).scalar() or 0

    return {
        "total_stores": total_stores,
        "active_stores": active_stores,
        "pending_stores": pending_stores,
        "suspended_stores": suspended_stores,
        "total_users": total_users,
        "total_revenue": round(total_revenue, 2),
        "total_orders": total_orders,
    }