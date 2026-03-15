from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.service_category import ServiceCategory
from app.schemas.service_category import ServiceCategoryCreate, ServiceCategoryUpdate


def create_category(db: Session, store_id: int, data: ServiceCategoryCreate) -> ServiceCategory:
    category = ServiceCategory(
        store_id=store_id,
        name=data.name,
        description=data.description,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_categories_by_store(db: Session, store_id: int, only_active: bool = True):
    query = db.query(ServiceCategory).filter(ServiceCategory.store_id == store_id)
    if only_active:
        query = query.filter(ServiceCategory.is_active == True)
    return query.all()


def get_category(db: Session, category_id: int) -> ServiceCategory:
    category = db.query(ServiceCategory).filter(ServiceCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return category


def update_category(db: Session, category: ServiceCategory, data: ServiceCategoryUpdate) -> ServiceCategory:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category: ServiceCategory):
    category.is_active = False
    db.commit()