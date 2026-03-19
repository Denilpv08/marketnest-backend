from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas.store import StoreResponse, StoreStatusUpdate
from app.schemas.user import UserResponse, UserCreate, UserUpdate, UserStatusUpdate
from app.services import store_service, user_service, auth_service
from app.middleware.auth import require_superadmin
from app.models.user import User

router = APIRouter(prefix="/api/admin", tags=["Superadmin"])


# --- Gestión de tiendas ---

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


# --- Gestión de usuarios ---

@router.get("/users", response_model=List[UserResponse])
def list_all_users(
    role: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Lista todos los usuarios con filtros opcionales."""
    return user_service.get_all_users(db, role=role, status=status)


@router.get("/users/pending", response_model=List[UserResponse])
def list_pending_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Lista los admins pendientes de aprobación."""
    from app.models.user import UserStatus
    return user_service.get_all_users(db, status=UserStatus.pending)


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Obtiene un usuario por ID."""
    return user_service.get_user_by_id(db, user_id)


@router.post("/users", response_model=UserResponse, status_code=201)
def create_admin_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Crea un usuario admin directamente aprobado."""
    from app.models.user import UserRole, UserStatus
    user = auth_service.register_user(db, data)
    # El superadmin crea admins ya aprobados
    if user.role == UserRole.admin:
        user.status = UserStatus.active
        db.commit()
        db.refresh(user)
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Edita los datos de un usuario."""
    user = user_service.get_user_by_id(db, user_id)
    return user_service.update_user(db, user, data)


@router.patch("/users/{user_id}/status", response_model=UserResponse)
def update_user_status(
    user_id: int,
    data: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Aprueba, suspende o activa un usuario."""
    return user_service.update_user_status(db, user_id, data.status)