from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.store import Store, StoreStatus
from app.models.subscription import StoreSubscription
from app.schemas.store import StoreCreate, StoreUpdate


def create_store(db: Session, store_data: StoreCreate, owner_id: int) -> Store:
    existing = db.query(Store).filter(Store.slug == store_data.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="El slug ya está en uso")

    store = Store(
        name=store_data.name,
        slug=store_data.slug,
        description=store_data.description,
        owner_id=owner_id,
        status=StoreStatus.pending,
    )
    db.add(store)
    db.flush()

    subscription = StoreSubscription(store_id=store.id)
    db.add(subscription)
    db.commit()
    db.refresh(store)
    return store


def get_store_by_slug(db: Session, slug: str) -> Store:
    store = db.query(Store).filter(
        Store.slug == slug,
        Store.is_active == True
    ).first()
    if not store:
        raise HTTPException(status_code=404, detail="Tienda no encontrada")
    return store


def get_store_by_id(db: Session, store_id: int) -> Store:
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Tienda no encontrada")
    return store


def update_store(db: Session, store: Store, data: StoreUpdate) -> Store:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(store, field, value)
    db.commit()
    db.refresh(store)
    return store


def get_all_stores(db: Session, status: StoreStatus = None):
    query = db.query(Store)
    if status:
        query = query.filter(Store.status == status)
    return query.all()


def change_store_status(db: Session, store_id: int, new_status: StoreStatus) -> Store:
    store = get_store_by_id(db, store_id)
    store.status = new_status
    db.commit()
    db.refresh(store)
    return store