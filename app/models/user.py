from sqlalchemy import Column, Integer, String, Enum, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


class UserRole(str, enum.Enum):
    superadmin = "superadmin"
    admin = "admin"
    customer = "customer"


class UserStatus(str, enum.Enum):
    active = "active"
    pending = "pending"       # Admin esperando aprobación
    suspended = "suspended"   # Suspendido por superadmin


class IdentityType(str, enum.Enum):
    cc = "cc"
    ce = "ce"
    passport = "passport"
    nit = "nit"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=True)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.customer, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.active, nullable=False)

    # Identidad
    identity_type = Column(Enum(IdentityType), nullable=True)
    identity_number = Column(String(50), nullable=True)

    # Ubicación
    city = Column(String(100), nullable=True)
    address = Column(String(255), nullable=True)

    # Foto
    photo_url = Column(String(500), nullable=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    store = relationship("Store", back_populates="owner", uselist=False)
    cart_items = relationship("CartItem", back_populates="user")
    orders = relationship("Order", back_populates="user")
    appointments = relationship("Appointment", back_populates="user")