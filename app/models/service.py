from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


class DurationUnit(str, enum.Enum):
    minutes = "minutes"
    hours = "hours"
    days = "days"


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("service_categories.id"), nullable=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)

    # Duración temporal
    duration = Column(Integer, nullable=False)
    duration_unit = Column(Enum(DurationUnit), default=DurationUnit.minutes)

    image_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    store = relationship("Store", back_populates="services")
    category = relationship("ServiceCategory", back_populates="services")
    appointments = relationship("Appointment", back_populates="service")