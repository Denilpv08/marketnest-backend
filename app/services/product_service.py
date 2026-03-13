from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


def create_product(db: Session, data: ProductCreate, store_id: int) -> Product:
    product = Product(**data.model_dump(), store_id=store_id)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def get_products_by_store(db: Session, store_id: int, only_active: bool = True):
    query = db.query(Product).filter(Product.store_id == store_id)
    if only_active:
        query = query.filter(Product.is_active == True)
    return query.all()


def get_product(db: Session, product_id: int) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


def update_product(db: Session, product: Product, data: ProductUpdate) -> Product:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product: Product):
    product.is_active = False
    db.commit()


def update_stock(db: Session, product_id: int, quantity: int) -> Product:
    product = get_product(db, product_id)
    if product.stock < quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Stock insuficiente. Disponible: {product.stock}"
        )
    product.stock -= quantity
    db.commit()
    db.refresh(product)
    return product