from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.service import Service
from app.schemas.service import ServiceCreate, ServiceUpdate


def create_service(db: Session, store_id: int, data: ServiceCreate) -> Service:
    if data.category_id:
        from app.models.service_category import ServiceCategory
        category = db.query(ServiceCategory).filter(
            ServiceCategory.id == data.category_id,
            ServiceCategory.store_id == store_id
        ).first()
        if not category:
            raise HTTPException(
                status_code=404,
                detail="Categoría no encontrada o no pertenece a esta tienda"
            )

    service = Service(
        store_id=store_id,
        **data.model_dump()
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


def get_services_by_store(db: Session, store_id: int, only_active: bool = True):
    query = db.query(Service).filter(Service.store_id == store_id)
    if only_active:
        query = query.filter(Service.is_active == True)
    return query.all()


def get_services_by_category(db: Session, category_id: int, only_active: bool = True):
    query = db.query(Service).filter(Service.category_id == category_id)
    if only_active:
        query = query.filter(Service.is_active == True)
    return query.all()


def get_service(db: Session, service_id: int) -> Service:
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return service


def update_service(db: Session, service: Service, data: ServiceUpdate) -> Service:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(service, field, value)
    db.commit()
    db.refresh(service)
    return service


def delete_service(db: Session, service: Service):
    service.is_active = False
    db.commit()