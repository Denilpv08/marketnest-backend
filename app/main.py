from fastapi import FastAPI
from app.config import settings
from app.middleware.cors import setup_cors
from app.routers import auth, stores, products, cart, orders, payments, dashboard, admin

app = FastAPI(
    title=settings.APP_NAME,
    description="API para gestión de establecimientos y e-commerce multi-tenant",
    version="1.0.0",
)

setup_cors(app)

app.include_router(auth.router)
app.include_router(stores.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(payments.router)
app.include_router(dashboard.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return {"message": f"Bienvenido a {settings.APP_NAME} API"}


@app.get("/health")
def health_check():
    return {"status": "ok"}