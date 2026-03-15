from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.user import UserUpdate, UserResponse
from app.services import user_service
from app.middleware.auth import get_current_user, require_superadmin
from app.models.user import User

router = APIRouter(prefix="/api/users", tags=["Usuarios"])


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """Obtiene el perfil completo del usuario autenticado."""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_my_profile(
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualiza el perfil del usuario autenticado."""
    return user_service.update_user(db, current_user, data)


@router.get("/", response_model=List[UserResponse])
def list_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Lista todos los usuarios del sistema (solo superadmin)."""
    return user_service.get_all_users(db)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Obtiene un usuario por ID (solo superadmin)."""
    return user_service.get_user_by_id(db, user_id)


@router.delete("/{user_id}", status_code=204)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Desactiva un usuario del sistema (solo superadmin)."""
    user = user_service.get_user_by_id(db, user_id)
    user_service.deactivate_user(db, user)