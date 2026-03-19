from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.user import User, UserRole, UserStatus
from app.schemas.user import UserUpdate


def get_user_by_id(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


def update_user(db: Session, user: User, data: UserUpdate) -> User:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def update_user_status(db: Session, user_id: int, status: UserStatus) -> User:
    user = get_user_by_id(db, user_id)

    if user.role == UserRole.superadmin:
        raise HTTPException(
            status_code=400,
            detail="No puedes modificar el estado de un superadmin"
        )

    user.status = status

    # Si se suspende también se desactiva
    if status == UserStatus.suspended:
        user.is_active = False
    elif status == UserStatus.active:
        user.is_active = True

    db.commit()
    db.refresh(user)
    return user


def get_all_users(db: Session, role: str = None, status: str = None):
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if status:
        query = query.filter(User.status == status)
    return query.order_by(User.created_at.desc()).all()


def deactivate_user(db: Session, user: User) -> User:
    user.is_active = False
    user.status = UserStatus.suspended
    db.commit()
    db.refresh(user)
    return user