from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentStatusUpdate, AppointmentResponse
from app.services import appointment_service
from app.middleware.auth import get_current_user, require_admin
from app.models.user import User, UserRole

router = APIRouter(prefix="/api/appointments", tags=["Citas"])


@router.post("/", response_model=AppointmentResponse, status_code=201)
def create_appointment(
    data: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Agenda una cita en una tienda."""
    return appointment_service.create_appointment(db, current_user.id, data)


@router.get("/my", response_model=List[AppointmentResponse])
def my_appointments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lista las citas del usuario autenticado."""
    return appointment_service.get_appointments_by_user(db, current_user.id)


@router.get("/store/{store_id}", response_model=List[AppointmentResponse])
def store_appointments(
    store_id: int,
    appointment_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Lista las citas de una tienda, opcionalmente filtradas por fecha (solo admin)."""
    return appointment_service.get_appointments_by_store(db, store_id, appointment_date)


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene una cita por ID."""
    appointment = appointment_service.get_appointment(db, appointment_id)
    if appointment.user_id != current_user.id and current_user.role not in [UserRole.admin, UserRole.superadmin]:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="No puedes ver esta cita")
    return appointment


@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    data: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualiza fecha, hora o notas de una cita (solo el cliente que la agendó)."""
    appointment = appointment_service.get_appointment(db, appointment_id)
    if appointment.user_id != current_user.id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="No puedes modificar esta cita")
    return appointment_service.update_appointment(db, appointment, data)


@router.patch("/{appointment_id}/status", response_model=AppointmentResponse)
def update_appointment_status(
    appointment_id: int,
    data: AppointmentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Confirma, cancela o completa una cita (solo admin)."""
    appointment = appointment_service.get_appointment(db, appointment_id)
    if appointment.store.owner_id != current_user.id and current_user.role != UserRole.superadmin:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="No puedes gestionar citas de otra tienda")
    return appointment_service.update_appointment_status(db, appointment, data)


@router.delete("/{appointment_id}", status_code=204)
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancela una cita (el cliente o el admin pueden cancelar)."""
    appointment = appointment_service.get_appointment(db, appointment_id)
    if appointment.user_id != current_user.id and current_user.role not in [UserRole.admin, UserRole.superadmin]:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="No puedes cancelar esta cita")
    appointment_service.cancel_appointment(db, appointment)