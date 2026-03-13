from fastapi import FastAPI
from app.config import settings
from app.middleware.cors import setup_cors

app = FastAPI(
    title=settings.APP_NAME,
    description="API para gestión de establecimientos y e-commerce multi-tenant",
    version="1.0.0",
)

setup_cors(app)


@app.get("/")
def root():
    return {"message": f"Bienvenido a {settings.APP_NAME} API"}


@app.get("/health")
def health_check():
    return {"status": "ok"}