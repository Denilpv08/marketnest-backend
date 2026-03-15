from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.store import Store, StoreStatus, StoreType
from app.models.subscription import StoreSubscription
from app.schemas.store import StoreCreate, StoreUpdate


def create_store(db: Session, store_data: StoreCreate, owner_id: int) -> Store:
    existing = db.query(Store).filter(Store.slug == store_data.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="El slug ya está en uso")

    # Validar custom_store_type cuando store_type es other
    if store_data.store_type == StoreType.other and not store_data.custom_store_type:
        raise HTTPException(
            status_code=400,
            detail="Debes especificar el tipo de tienda cuando seleccionas 'Otro'"
        )

    # Validar que custom_store_type solo se use con store_type other
    if store_data.store_type != StoreType.other and store_data.custom_store_type:
        store_data.custom_store_type = None

    store = Store(
        name=store_data.name,
        slug=store_data.slug,
        description=store_data.description,
        owner_id=owner_id,
        status=StoreStatus.pending,
        store_type=store_data.store_type,
        custom_store_type=store_data.custom_store_type,
        business_type=store_data.business_type,
        tax_id=store_data.tax_id,
        phone=store_data.phone,
        contact_email=store_data.contact_email,
        city=store_data.city,
        address=store_data.address,
        latitude=store_data.latitude,
        longitude=store_data.longitude,
        opening_hours=store_data.opening_hours,
        allows_appointments=store_data.allows_appointments,
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
    # Validar custom_store_type si se está actualizando store_type
    update_data = data.model_dump(exclude_unset=True)

    new_store_type = update_data.get("store_type", store.store_type)
    new_custom_type = update_data.get("custom_store_type", store.custom_store_type)

    if new_store_type == StoreType.other and not new_custom_type:
        raise HTTPException(
            status_code=400,
            detail="Debes especificar el tipo de tienda cuando seleccionas 'Otro'"
        )
    if new_store_type != StoreType.other:
        update_data["custom_store_type"] = None

    for field, value in update_data.items():
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