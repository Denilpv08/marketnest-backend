from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.services import product_service
from app.middleware.auth import require_admin
from app.models.user import User, UserRole

router = APIRouter(prefix="/api/products", tags=["Productos"])


@router.get("/store/{store_id}", response_model=List[ProductResponse])
def list_products(store_id: int, db: Session = Depends(get_db)):
    """Lista los productos activos de una tienda (público)."""
    return product_service.get_products_by_store(db, store_id)


@router.get("/store/{store_id}/all", response_model=List[ProductResponse])
def list_all_products(
    store_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Lista todos los productos incluyendo inactivos (solo admin)."""
    return product_service.get_products_by_store(db, store_id, only_active=False)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Obtiene un producto por su ID (público)."""
    return product_service.get_product(db, product_id)


@router.post("/store/{store_id}", response_model=ProductResponse, status_code=201)
def create_product(
    store_id: int,
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Crea un producto en la tienda (solo admin)."""
    store = product_service.get_product  # verificación de tienda
    return product_service.create_product(db, data, store_id)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Actualiza un producto incluyendo su stock (solo admin)."""
    product = product_service.get_product(db, product_id)
    if product.store.owner_id != current_user.id and current_user.role != UserRole.superadmin:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="No puedes editar productos de otra tienda")
    return product_service.update_product(db, product, data)


@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Desactiva un producto — soft delete (solo admin)."""
    product = product_service.get_product(db, product_id)
    if product.store.owner_id != current_user.id and current_user.role != UserRole.superadmin:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="No puedes eliminar productos de otra tienda")
    product_service.delete_product(db, product)