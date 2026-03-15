from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum, Date, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


class AppointmentStatus(str, enum.Enum):
    pending = "pending"         # Agendada, esperando confirmación
    confirmed = "confirmed"     # Confirmada por el admin
    cancelled = "cancelled"     # Cancelada
    completed = "completed"     # Completada


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=True)  # Opcional

    # Fecha y hora
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)

    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.pending)
    notes = Column(Text, nullable=True)         # Notas del cliente
    admin_notes = Column(Text, nullable=True)   # Notas internas del admin

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    store = relationship("Store", back_populates="appointments")
    user = relationship("User", back_populates="appointments")
    service = relationship("Service", back_populates="appointments")