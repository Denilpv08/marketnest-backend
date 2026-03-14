from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import dashboard_service
from app.middleware.auth import require_admin, require_superadmin
from app.models.user import User

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/store/{store_id}")
def store_dashboard(
    store_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Estadísticas de ventas de la tienda (solo admins)."""
    return dashboard_service.get_store_dashboard(db, store_id)


@router.get("/superadmin")
def superadmin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Estadísticas globales del sistema (solo superadmin)."""
    return dashboard_service.get_superadmin_dashboard(db)