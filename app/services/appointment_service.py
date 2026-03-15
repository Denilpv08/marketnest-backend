from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import date

from app.models.appointment import Appointment, AppointmentStatus
from app.models.store import Store
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentStatusUpdate


def create_appointment(db: Session, user_id: int, data: AppointmentCreate) -> Appointment:
    store = db.query(Store).filter(
        Store.id == data.store_id,
        Store.is_active == True
    ).first()
    if not store:
        raise HTTPException(status_code=404, detail="Tienda no encontrada")
    if not store.allows_appointments:
        raise HTTPException(
            status_code=400,
            detail="Esta tienda no permite agendar citas"
        )

    if data.date < date.today():
        raise HTTPException(
            status_code=400,
            detail="No puedes agendar una cita en una fecha pasada"
        )

    if data.service_id:
        from app.models.service import Service
        service = db.query(Service).filter(
            Service.id == data.service_id,
            Service.store_id == data.store_id,
            Service.is_active == True
        ).first()
        if not service:
            raise HTTPException(
                status_code=404,
                detail="Servicio no encontrado o no pertenece a esta tienda"
            )

    appointment = Appointment(
        store_id=data.store_id,
        user_id=user_id,
        service_id=data.service_id,
        date=data.date,
        time=data.time,
        notes=data.notes,
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


def get_appointments_by_user(db: Session, user_id: int):
    return db.query(Appointment).filter(Appointment.user_id == user_id).all()


def get_appointments_by_store(db: Session, store_id: int, appointment_date: date = None):
    query = db.query(Appointment).filter(Appointment.store_id == store_id)
    if appointment_date:
        query = query.filter(Appointment.date == appointment_date)
    return query.order_by(Appointment.date, Appointment.time).all()


def get_appointment(db: Session, appointment_id: int) -> Appointment:
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    return appointment


def update_appointment(db: Session, appointment: Appointment, data: AppointmentUpdate) -> Appointment:
    if appointment.status in [AppointmentStatus.cancelled, AppointmentStatus.completed]:
        raise HTTPException(
            status_code=400,
            detail="No puedes modificar una cita cancelada o completada"
        )
    if data.date and data.date < date.today():
        raise HTTPException(
            status_code=400,
            detail="No puedes agendar una cita en una fecha pasada"
        )
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(appointment, field, value)
    db.commit()
    db.refresh(appointment)
    return appointment


def update_appointment_status(
    db: Session,
    appointment: Appointment,
    data: AppointmentStatusUpdate
) -> Appointment:
    if appointment.status == AppointmentStatus.completed:
        raise HTTPException(
            status_code=400,
            detail="No puedes modificar una cita ya completada"
        )
    appointment.status = data.status
    if data.admin_notes:
        appointment.admin_notes = data.admin_notes
    db.commit()
    db.refresh(appointment)
    return appointment


def cancel_appointment(db: Session, appointment: Appointment) -> Appointment:
    if appointment.status in [AppointmentStatus.completed, AppointmentStatus.cancelled]:
        raise HTTPException(
            status_code=400,
            detail="Esta cita no puede ser cancelada"
        )
    appointment.status = AppointmentStatus.cancelled
    db.commit()
    db.refresh(appointment)
    return appointment