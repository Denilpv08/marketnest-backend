from sqlalchemy import Column, Integer, String, Enum, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


class StoreStatus(str, enum.Enum):
    pending = "pending"       # Esperando aprobación del superadmin
    active = "active"         # Tienda activa y visible
    suspended = "suspended"   # Suspendida por el superadmin


class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(StoreStatus), default=StoreStatus.pending)

    # Personalización visual
    logo_url = Column(String(500), nullable=True)
    primary_color = Column(String(7), default="#3B82F6")
    secondary_color = Column(String(7), default="#1E40AF")
    banner_url = Column(String(500), nullable=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    owner = relationship("User", back_populates="store")
    products = relationship("Product", back_populates="store")
    orders = relationship("Order", back_populates="store")
    subscription = relationship("StoreSubscription", back_populates="store", uselist=False)