from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.store import StoreResponse, StoreStatusUpdate
from app.services import store_service
from app.middleware.auth import require_superadmin
from app.models.user import User

router = APIRouter(prefix="/api/admin", tags=["Superadmin"])


@router.get("/stores", response_model=List[StoreResponse])
def list_all_stores(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Lista todos los establecimientos del sistema."""
    return store_service.get_all_stores(db)


@router.get("/stores/pending", response_model=List[StoreResponse])
def list_pending_stores(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Lista las solicitudes pendientes de aprobación."""
    from app.models.store import StoreStatus
    return store_service.get_all_stores(db, status=StoreStatus.pending)


@router.patch("/stores/{store_id}/status", response_model=StoreResponse)
def change_store_status(
    store_id: int,
    data: StoreStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Aprueba, suspende o activa un establecimiento."""
    return store_service.change_store_status(db, store_id, data.status)


@router.get("/dashboard")
def admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Estadísticas globales del sistema."""
    from app.services import dashboard_service
    return dashboard_service.get_superadmin_dashboard(db)