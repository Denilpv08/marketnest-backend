from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.services import auth_service
from app.middleware.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Registra un nuevo usuario y devuelve el token."""
    user = auth_service.register_user(db, user_data)
    token = auth_service.create_access_token(user.id)
    return {"access_token": token, "user": user}


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Inicia sesión con JSON — usar desde el frontend."""
    user = auth_service.authenticate_user(db, credentials.email, credentials.password)
    token = auth_service.create_access_token(user.id)
    return {"access_token": token, "user": user}


@router.post("/token", response_model=TokenResponse)
def login_swagger(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Inicia sesión con form-data — usado por Swagger."""
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    token = auth_service.create_access_token(user.id)
    return {"access_token": token, "user": user}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Devuelve el perfil del usuario autenticado."""
    return current_user