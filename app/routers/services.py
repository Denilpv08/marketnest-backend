from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.service_category import ServiceCategoryCreate, ServiceCategoryUpdate, ServiceCategoryResponse
from app.schemas.service import ServiceCreate, ServiceUpdate, ServiceResponse
from app.services import service_category_service, service_service
from app.middleware.auth import get_current_user, require_admin
from app.models.user import User, UserRole

router = APIRouter(prefix="/api/services", tags=["Servicios"])


# --- Categorías ---

@router.get("/store/{store_id}/categories", response_model=List[ServiceCategoryResponse])
def list_categories(store_id: int, db: Session = Depends(get_db)):
    """Lista las categorías de servicios de una tienda (público)."""
    return service_category_service.get_categories_by_store(db, store_id)


@router.post("/store/{store_id}/categories", response_model=ServiceCategoryResponse, status_code=201)
def create_category(
    store_id: int,
    data: ServiceCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Crea una categoría de servicios (solo admin)."""
    return service_category_service.create_category(db, store_id, data)


@router.put("/categories/{category_id}", response_model=ServiceCategoryResponse)
def update_category(
    category_id: int,
    data: ServiceCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Actualiza una categoría (solo admin)."""
    category = service_category_service.get_category(db, category_id)
    if category.store.owner_id != current_user.id and current_user.role != UserRole.superadmin:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="No puedes editar categorías de otra tienda")
    return service_category_service.update_category(db, category, data)


@router.delete("/categories/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Desactiva una categoría (solo admin)."""
    category = service_category_service.get_category(db, category_id)
    if category.store.owner_id != current_user.id and current_user.role != UserRole.superadmin:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="No puedes eliminar categorías de otra tienda")
    service_category_service.delete_category(db, category)


# --- Servicios ---

@router.get("/store/{store_id}", response_model=List[ServiceResponse])
def list_services(store_id: int, db: Session = Depends(get_db)):
    """Lista los servicios activos de una tienda (público)."""
    return service_service.get_services_by_store(db, store_id)


@router.get("/category/{category_id}", response_model=List[ServiceResponse])
def list_services_by_category(category_id: int, db: Session = Depends(get_db)):
    """Lista los servicios de una categoría (público)."""
    return service_service.get_services_by_category(db, category_id)


@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(service_id: int, db: Session = Depends(get_db)):
    """Obtiene un servicio por ID (público)."""
    return service_service.get_service(db, service_id)


@router.post("/store/{store_id}", response_model=ServiceResponse, status_code=201)
def create_service(
    store_id: int,
    data: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Crea un servicio en la tienda (solo admin)."""
    return service_service.create_service(db, store_id, data)


@router.put("/{service_id}", response_model=ServiceResponse)
def update_service(
    service_id: int,
    data: ServiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Actualiza un servicio (solo admin)."""
    service = service_service.get_service(db, service_id)
    if service.store.owner_id != current_user.id and current_user.role != UserRole.superadmin:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="No puedes editar servicios de otra tienda")
    return service_service.update_service(db, service, data)


@router.delete("/{service_id}", status_code=204)
def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Desactiva un servicio (solo admin)."""
    service = service_service.get_service(db, service_id)
    if service.store.owner_id != current_user.id and current_user.role != UserRole.superadmin:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="No puedes eliminar servicios de otra tienda")
    service_service.delete_service(db, service)