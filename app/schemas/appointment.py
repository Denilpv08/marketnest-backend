from pydantic import BaseModel
from datetime import datetime, date as dt_date, time as dt_time
from typing import Optional
from app.models.appointment import AppointmentStatus
from app.schemas.service import ServiceResponse


# --- Esquemas de entrada ---

class AppointmentCreate(BaseModel):
    store_id: int
    service_id: Optional[int] = None
    date: dt_date
    time: dt_time
    notes: Optional[str] = None


class AppointmentUpdate(BaseModel):
    date: Optional[dt_date] = None
    time: Optional[dt_time] = None
    notes: Optional[str] = None


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus
    admin_notes: Optional[str] = None


# --- Esquemas de salida ---

class AppointmentResponse(BaseModel):
    id: int
    store_id: int
    user_id: int
    service_id: Optional[int]
    date: dt_date
    time: dt_time
    status: AppointmentStatus
    notes: Optional[str]
    admin_notes: Optional[str]
    service: Optional[ServiceResponse]
    created_at: datetime

    class Config:
        from_attributes = True