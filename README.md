# MarketNest Backend

SaaS multi-tenant para gestión de tiendas online con FastAPI y MySQL.

## Requisitos

- Python 3.11+
- MySQL 8.0+

## Instalación

```bash
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar entorno (Windows)
venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
copy .env.example .env
# Edita .env con tus credenciales

# 5. Crear la base de datos en MySQL
# CREATE DATABASE marketnest;

# 6. Ejecutar migraciones
alembic upgrade head

# 7. Levantar el servidor
uvicorn app.main:app --reload
```

## Documentación

Disponible en: http://localhost:8000/docs

## Roles

- `superadmin` — Control total del sistema
- `admin` — Gestiona su tienda
- `customer` — Comprador
