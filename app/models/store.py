from sqlalchemy import Column, Integer, String, Enum, DateTime, Boolean, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


class StoreStatus(str, enum.Enum):
    pending = "pending"
    active = "active"
    suspended = "suspended"


class StoreType(str, enum.Enum):
    restaurant = "restaurant"
    liquor_store = "liquor_store"
    clothing = "clothing"
    barbershop = "barbershop"
    pharmacy = "pharmacy"
    hardware_store = "hardware_store"
    other = "other"


class BusinessType(str, enum.Enum):
    products = "products"                     # Solo vende productos
    services = "services"                     # Solo ofrece servicios
    products_services = "products_services"   # Ambos


class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(StoreStatus), default=StoreStatus.pending)

    # Tipo de negocio
    store_type = Column(Enum(StoreType), nullable=True)
    custom_store_type = Column(String(100), nullable=True)  # Cuando store_type = other
    business_type = Column(Enum(BusinessType), default=BusinessType.products)

    # Información de contacto
    tax_id = Column(String(50), nullable=True)       # NIT
    phone = Column(String(20), nullable=True)
    contact_email = Column(String(150), nullable=True)
    city = Column(String(100), nullable=True)
    address = Column(String(255), nullable=True)

    # Coordenadas para mapa
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Horarios de atención (JSON)
    # Ejemplo: {"monday": {"open": "08:00", "close": "18:00"}, "sunday": null}
    opening_hours = Column(JSON, nullable=True)

    # Citas
    allows_appointments = Column(Boolean, default=False)

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
    service_categories = relationship("ServiceCategory", back_populates="store")
    services = relationship("Service", back_populates="store")
    appointments = relationship("Appointment", back_populates="store")