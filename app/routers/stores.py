from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.store import StoreCreate, StoreUpdate, StoreResponse
from app.services import store_service
from app.middleware.auth import get_current_user, require_admin
from app.models.user import User, UserRole

router = APIRouter(prefix="/api/stores", tags=["Tiendas"])


@router.post("/", response_model=StoreResponse, status_code=201)
def create_store(
    data: StoreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Solicita crear una nueva tienda (queda en estado pending)."""
    return store_service.create_store(db, data, current_user.id)


@router.get("/", response_model=List[StoreResponse])
def list_my_stores(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lista las tiendas del usuario autenticado."""
    stores = store_service.get_all_stores(db)
    return [s for s in stores if s.owner_id == current_user.id]

@router.get("/public", response_model=List[StoreResponse])
def list_public_stores(db: Session = Depends(get_db)):
    """Lista todas las tiendas activas (público)."""
    from app.models.store import StoreStatus
    stores = store_service.get_all_stores(db, status=StoreStatus.active)
    return stores

@router.get("/{slug}", response_model=StoreResponse)
def get_store(slug: str, db: Session = Depends(get_db)):
    """Obtiene una tienda por su slug (público)."""
    return store_service.get_store_by_slug(db, slug)


@router.put("/{store_id}", response_model=StoreResponse)
def update_store(
    store_id: int,
    data: StoreUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Actualiza los datos y personalización de la tienda."""
    store = store_service.get_store_by_id(db, store_id)
    if store.owner_id != current_user.id and current_user.role != UserRole.superadmin:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="No puedes editar esta tienda")
    return store_service.update_store(db, store, data)