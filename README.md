# MarketNest Backend

API REST construida con **FastAPI** y **MySQL** para gestión de establecimientos y e-commerce multi-tenant. Permite a negocios crear su propia tienda online dentro de una plataforma centralizada, con soporte para productos, servicios y agendamiento de citas.

---

## 📋 Tabla de contenidos

- [Descripción general](#descripción-general)
- [Stack tecnológico](#stack-tecnológico)
- [Arquitectura](#arquitectura)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Base de datos](#base-de-datos)
- [Roles y estados del sistema](#roles-y-estados-del-sistema)
- [Instalación y configuración](#instalación-y-configuración)
- [Migraciones](#migraciones)
- [Endpoints](#endpoints)
- [Autenticación](#autenticación)
- [Comandos útiles](#comandos-útiles)

---

## Descripción general

MarketNest es un SaaS (Software as a Service) multi-tenant donde:

- **Tú** (superadmin) controlas la plataforma — apruebas o rechazas solicitudes de establecimientos y usuarios admin, gestionas suscripciones y monitoreas el sistema completo.
- **Los negocios** (admins) solicitan su cuenta, esperan aprobación, crean su tienda, publican productos y/o servicios, gestionan inventario, personalizan colores y logo, ven estadísticas de ventas y gestionan citas.
- **Los compradores** (customers) navegan tiendas, agregan productos al carrito, realizan compras con Stripe y agendan citas.

---

## Stack tecnológico

| Herramienta       | Versión | Propósito                                    |
| ----------------- | ------- | -------------------------------------------- |
| Python            | 3.12    | Lenguaje principal                           |
| FastAPI           | 0.111.0 | Framework web                                |
| Uvicorn           | 0.29.0  | Servidor ASGI                                |
| SQLAlchemy        | 2.0.30  | ORM — mapeo de modelos a tablas              |
| Alembic           | 1.13.1  | Migraciones de base de datos                 |
| PyMySQL           | 1.1.1   | Driver de conexión a MySQL                   |
| Pydantic          | 2.7.1   | Validación de datos de entrada y salida      |
| pydantic-settings | 2.2.1   | Lectura de variables de entorno              |
| python-jose       | 3.3.0   | Generación y decodificación de JWT           |
| passlib + argon2  | 1.7.4   | Hasheo seguro de contraseñas                 |
| argon2-cffi       | 23.1.0  | Backend de hasheo compatible con Python 3.12 |
| Stripe            | 9.9.0   | Pasarela de pagos                            |
| python-dotenv     | 1.0.1   | Carga del archivo .env                       |

---

## Arquitectura

```
Frontend (Next.js)
       │
       │ HTTP / REST
       ▼
FastAPI (Backend)
  ├── Routers       → Reciben las peticiones HTTP
  ├── Services      → Lógica de negocio
  ├── Models        → Definición de tablas (SQLAlchemy)
  ├── Schemas       → Validación de datos (Pydantic)
  └── Middleware    → Seguridad JWT y CORS
       │
       ▼
MySQL (Base de datos)
```

**Flujo de una petición:**

1. El frontend envía una petición HTTP
2. El router recibe la petición y valida los datos con el schema
3. El middleware verifica el token JWT si el endpoint lo requiere
4. El router llama al service correspondiente
5. El service ejecuta la lógica de negocio y consulta la BD
6. La respuesta regresa al frontend formateada por el schema de salida

---

## Estructura del proyecto

```
marketnest/
│
├── app/
│   ├── main.py              # Punto de entrada — registra routers y middleware
│   ├── config.py            # Lee variables del .env con Pydantic Settings
│   ├── database.py          # Conexión a MySQL, sesiones y Base para modelos
│   │
│   ├── models/              # Tablas de la base de datos (SQLAlchemy)
│   │   ├── __init__.py      # Importa todos los modelos para Alembic
│   │   ├── user.py          # Tabla users + enums UserRole, UserStatus, IdentityType
│   │   ├── store.py         # Tabla stores + enums StoreStatus, StoreType, BusinessType
│   │   ├── subscription.py  # Tabla store_subscriptions + enums de plan
│   │   ├── product.py       # Tabla products
│   │   ├── cart.py          # Tabla cart_items
│   │   ├── order.py         # Tablas orders + order_items + enum OrderStatus
│   │   ├── payment.py       # Tabla payments + enum PaymentStatus
│   │   ├── service_category.py  # Tabla service_categories
│   │   ├── service.py       # Tabla services + enum DurationUnit
│   │   └── appointment.py   # Tabla appointments + enum AppointmentStatus
│   │
│   ├── schemas/             # Validación de datos con Pydantic
│   │   ├── __init__.py
│   │   ├── user.py          # UserCreate, UserLogin, UserUpdate, UserStatusUpdate, UserResponse, TokenResponse
│   │   ├── store.py         # StoreCreate, StoreUpdate, StoreResponse, DaySchedule
│   │   ├── product.py       # ProductCreate, ProductUpdate, ProductResponse
│   │   ├── cart.py          # CartItemCreate, CartItemUpdate, CartResponse
│   │   ├── order.py         # OrderResponse, OrderStatusUpdate
│   │   ├── payment.py       # PaymentCreate, CheckoutResponse, PaymentResponse
│   │   ├── service_category.py  # ServiceCategoryCreate, ServiceCategoryUpdate, ServiceCategoryResponse
│   │   ├── service.py       # ServiceCreate, ServiceUpdate, ServiceResponse
│   │   └── appointment.py   # AppointmentCreate, AppointmentUpdate, AppointmentStatusUpdate, AppointmentResponse
│   │
│   ├── routers/             # Endpoints agrupados por dominio
│   │   ├── __init__.py
│   │   ├── auth.py          # /api/auth — registro, login, perfil
│   │   ├── users.py         # /api/users — perfil del usuario autenticado
│   │   ├── stores.py        # /api/stores — gestión de tiendas
│   │   ├── products.py      # /api/products — productos e inventario
│   │   ├── cart.py          # /api/cart — carrito de compras
│   │   ├── orders.py        # /api/orders — órdenes de compra
│   │   ├── payments.py      # /api/payments — pagos con Stripe
│   │   ├── dashboard.py     # /api/dashboard — estadísticas
│   │   ├── admin.py         # /api/admin — panel superadmin (tiendas + usuarios)
│   │   ├── services.py      # /api/services — categorías y servicios
│   │   └── appointments.py  # /api/appointments — agendamiento de citas
│   │
│   ├── services/            # Lógica de negocio separada de los routers
│   │   ├── __init__.py
│   │   ├── auth_service.py             # Hasheo, JWT, registro, autenticación
│   │   ├── user_service.py             # Actualización de perfil, gestión de usuarios, estados
│   │   ├── store_service.py            # CRUD de tiendas, validaciones, aprobación
│   │   ├── product_service.py          # CRUD de productos, inventario
│   │   ├── cart_service.py             # Agregar, quitar, vaciar carrito
│   │   ├── order_service.py            # Crear orden desde carrito, estados
│   │   ├── payment_service.py          # Integración Stripe, webhooks
│   │   ├── dashboard_service.py        # Estadísticas de tienda y sistema
│   │   ├── service_category_service.py # CRUD de categorías de servicios
│   │   ├── service_service.py          # CRUD de servicios
│   │   └── appointment_service.py      # Agendamiento, confirmación, cancelación
│   │
│   └── middleware/          # Seguridad transversal
│       ├── auth.py          # Verificación JWT, control de roles
│       └── cors.py          # Configuración CORS para el frontend
│
├── alembic/                 # Sistema de migraciones
│   ├── env.py               # Configuración de Alembic — conecta con los modelos
│   ├── script.py.mako       # Plantilla para generar archivos de migración
│   └── versions/            # Archivos de migración generados
│       ├── 1d6e78cac995_initial_migration.py
│       ├── ba197733d3f4_add_new_fields_and_tables.py
│       └── 8c9cf96e4b6d_add_user_status.py
│
├── .env                     # Variables de entorno — NO subir a Git
├── .env.example             # Plantilla del .env — SÍ subir a Git
├── .gitignore               # Archivos excluidos del repositorio
├── alembic.ini              # Configuración base de Alembic
└── requirements.txt         # Dependencias del proyecto
```

---

## Base de datos

### Tablas del sistema — 11 tablas

```
users
├── id (PK)
├── name
├── last_name
├── email (unique)
├── password_hash
├── role: superadmin | admin | customer
├── status: active | pending | suspended
├── identity_type: cc | ce | passport | nit
├── identity_number
├── city
├── address
├── photo_url
├── is_active
├── created_at
└── updated_at

stores
├── id (PK)
├── name
├── slug (unique)
├── description
├── owner_id (FK → users.id)
├── status: pending | active | suspended
├── store_type: restaurant | liquor_store | clothing | barbershop | pharmacy | hardware_store | other
├── custom_store_type   ← Solo cuando store_type = other
├── business_type: products | services | products_services
├── tax_id              ← NIT o número tributario
├── phone
├── contact_email
├── city
├── address
├── latitude            ← Coordenada para mapa
├── longitude           ← Coordenada para mapa
├── opening_hours       ← JSON con horarios por día
├── allows_appointments ← Activa el sistema de citas
├── logo_url
├── primary_color
├── secondary_color
├── banner_url
├── is_active
├── created_at
└── updated_at

store_subscriptions
├── id (PK)
├── store_id (FK → stores.id, unique)
├── plan: free | basic | pro
├── status: active | cancelled | expired
├── expires_at
├── created_at
└── updated_at

products
├── id (PK)
├── store_id (FK → stores.id)
├── name
├── description
├── price
├── stock
├── image_url
├── is_active
├── created_at
└── updated_at

service_categories
├── id (PK)
├── store_id (FK → stores.id)
├── name
├── description
├── is_active
├── created_at
└── updated_at

services
├── id (PK)
├── store_id (FK → stores.id)
├── category_id (FK → service_categories.id, opcional)
├── name
├── description
├── price
├── duration
├── duration_unit: minutes | hours | days
├── image_url
├── is_active
├── created_at
└── updated_at

appointments
├── id (PK)
├── store_id (FK → stores.id)
├── user_id (FK → users.id)
├── service_id (FK → services.id, opcional)
├── date
├── time
├── status: pending | confirmed | cancelled | completed
├── notes           ← Notas del cliente
├── admin_notes     ← Notas internas del admin
├── created_at
└── updated_at

cart_items
├── id (PK)
├── user_id (FK → users.id)
├── product_id (FK → products.id)
├── quantity
├── created_at
└── updated_at

orders
├── id (PK)
├── user_id (FK → users.id)
├── store_id (FK → stores.id)
├── total_amount
├── status: pending | paid | processing | shipped | delivered | cancelled
├── created_at
└── updated_at

order_items
├── id (PK)
├── order_id (FK → orders.id)
├── product_id (FK → products.id)
├── quantity
├── unit_price  ← snapshot del precio al momento de compra
└── created_at

payments
├── id (PK)
├── order_id (FK → orders.id, unique)
├── stripe_payment_id
├── amount
├── status: pending | succeeded | failed | refunded
├── created_at
└── updated_at
```

---

## Roles y estados del sistema

### Roles

| Rol          | Descripción                 | Permisos                                                                 |
| ------------ | --------------------------- | ------------------------------------------------------------------------ |
| `superadmin` | Dueño del sistema           | Todo — gestionar usuarios, tiendas, ver estadísticas globales            |
| `admin`      | Dueño de un establecimiento | Gestionar su tienda, productos, servicios, órdenes, citas y estadísticas |
| `customer`   | Comprador / cliente         | Navegar tiendas, agregar al carrito, comprar, agendar citas              |

### Estados de usuario (`UserStatus`)

| Estado      | Descripción                               | Puede iniciar sesión |
| ----------- | ----------------------------------------- | -------------------- |
| `active`    | Usuario activo y aprobado                 | ✅ Sí                |
| `pending`   | Admin esperando aprobación del superadmin | ❌ No                |
| `suspended` | Suspendido por el superadmin              | ❌ No                |

### Flujo de registro de un admin

```
Admin se registra → status: pending → No puede iniciar sesión
       ↓
Superadmin aprueba → status: active → Puede iniciar sesión y crear tienda
       ↓
Admin crea tienda → store.status: pending → Tienda no visible
       ↓
Superadmin aprueba tienda → store.status: active → Tienda visible
```

### Estados de tienda (`StoreStatus`)

| Estado      | Descripción                           |
| ----------- | ------------------------------------- |
| `pending`   | Esperando aprobación del superadmin   |
| `active`    | Tienda activa y visible para clientes |
| `suspended` | Suspendida por el superadmin          |

---

## Instalación y configuración

### Requisitos previos

- Python 3.12+
- MySQL 8.0+
- pip

### Pasos

**1. Clonar el repositorio**

```bash
git clone <url-del-repo>
cd marketnest
```

**2. Crear el entorno virtual**

```bash
python -m venv venv
```

**3. Activar el entorno virtual**

Windows:

```bash
venv\Scripts\activate
```

Mac / Linux:

```bash
source venv/bin/activate
```

**4. Instalar dependencias**

```bash
pip install -r requirements.txt
```

**5. Configurar variables de entorno**

```bash
copy .env.example .env   # Windows
cp .env.example .env     # Mac/Linux
```

Edita el `.env` con tus credenciales:

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=marketnest
DB_USER=root
DB_PASSWORD=tu_password

SECRET_KEY=una_clave_secreta_muy_larga_y_segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

STRIPE_SECRET_KEY=sk_test_xxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxx

APP_NAME=MarketNest
DEBUG=True
```

**6. Crear la base de datos en MySQL**

```sql
CREATE DATABASE marketnest CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

**7. Ejecutar migraciones**

```bash
alembic revision --autogenerate -m "initial migration"
alembic upgrade head
```

**8. Levantar el servidor**

```bash
uvicorn app.main:app --reload
```

El servidor corre en `http://localhost:8000`
La documentación Swagger está en `http://localhost:8000/docs`

---

## Migraciones

### Historial de migraciones del proyecto

| Revisión       | Descripción               | Cambios                                                                                                       |
| -------------- | ------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `1d6e78cac995` | initial migration         | Crea las tablas base: users, stores, store_subscriptions, products, cart_items, orders, order_items, payments |
| `ba197733d3f4` | add new fields and tables | Agrega campos a users y stores, crea tablas service_categories, services, appointments                        |
| `8c9cf96e4b6d` | add user status           | Agrega campo status a la tabla users con enum active/pending/suspended                                        |

### Comandos principales

**Generar una migración nueva**

```bash
alembic revision --autogenerate -m "descripcion del cambio"
```

**Aplicar migraciones pendientes**

```bash
alembic upgrade head
```

**Revertir la última migración**

```bash
alembic downgrade -1
```

**Ver el historial de migraciones**

```bash
alembic history
```

**Ver la migración actual**

```bash
alembic current
```

**Revertir todas las migraciones**

```bash
alembic downgrade base
```

### Flujo de trabajo al modificar un modelo

1. Modifica el archivo del modelo en `app/models/`
2. Genera la migración: `alembic revision --autogenerate -m "descripcion del cambio"`
3. Revisa el archivo generado en `alembic/versions/`
4. Aplica la migración: `alembic upgrade head`

---

## Endpoints

### Autenticación — `/api/auth`

| Método | Endpoint             | Descripción                           | Auth |
| ------ | -------------------- | ------------------------------------- | ---- |
| POST   | `/api/auth/register` | Registra un nuevo usuario             | No   |
| POST   | `/api/auth/login`    | Inicia sesión con JSON                | No   |
| POST   | `/api/auth/token`    | Inicia sesión con form-data (Swagger) | No   |
| GET    | `/api/auth/me`       | Perfil del usuario autenticado        | Sí   |

### Usuarios — `/api/users`

| Método | Endpoint        | Descripción                             | Auth |
| ------ | --------------- | --------------------------------------- | ---- |
| GET    | `/api/users/me` | Perfil completo del usuario             | Sí   |
| PUT    | `/api/users/me` | Actualiza perfil e información personal | Sí   |

### Tiendas — `/api/stores`

| Método | Endpoint                 | Descripción                        | Auth  |
| ------ | ------------------------ | ---------------------------------- | ----- |
| POST   | `/api/stores/`           | Solicita crear una tienda          | Sí    |
| GET    | `/api/stores/`           | Lista mis tiendas                  | Sí    |
| GET    | `/api/stores/public`     | Lista tiendas activas (público)    | No    |
| GET    | `/api/stores/{slug}`     | Obtiene una tienda por slug        | No    |
| PUT    | `/api/stores/{store_id}` | Actualiza tienda y personalización | Admin |

### Productos — `/api/products`

| Método | Endpoint                             | Descripción                | Auth  |
| ------ | ------------------------------------ | -------------------------- | ----- |
| GET    | `/api/products/store/{store_id}`     | Lista productos activos    | No    |
| GET    | `/api/products/store/{store_id}/all` | Lista todos los productos  | Admin |
| GET    | `/api/products/{product_id}`         | Obtiene un producto        | No    |
| POST   | `/api/products/store/{store_id}`     | Crea un producto           | Admin |
| PUT    | `/api/products/{product_id}`         | Actualiza producto / stock | Admin |
| DELETE | `/api/products/{product_id}`         | Desactiva un producto      | Admin |

### Carrito — `/api/cart`

| Método | Endpoint              | Descripción                 | Auth |
| ------ | --------------------- | --------------------------- | ---- |
| GET    | `/api/cart/`          | Ver carrito con total       | Sí   |
| POST   | `/api/cart/`          | Agregar producto al carrito | Sí   |
| PUT    | `/api/cart/{item_id}` | Actualizar cantidad         | Sí   |
| DELETE | `/api/cart/{item_id}` | Eliminar ítem del carrito   | Sí   |
| DELETE | `/api/cart/`          | Vaciar todo el carrito      | Sí   |

### Órdenes — `/api/orders`

| Método | Endpoint                        | Descripción                  | Auth  |
| ------ | ------------------------------- | ---------------------------- | ----- |
| POST   | `/api/orders/`                  | Crear orden desde el carrito | Sí    |
| GET    | `/api/orders/my`                | Historial de mis órdenes     | Sí    |
| GET    | `/api/orders/{order_id}`        | Ver una orden específica     | Sí    |
| GET    | `/api/orders/store/{store_id}`  | Órdenes de la tienda         | Admin |
| PATCH  | `/api/orders/{order_id}/status` | Actualizar estado de orden   | Admin |

### Pagos — `/api/payments`

| Método | Endpoint                         | Descripción               | Auth              |
| ------ | -------------------------------- | ------------------------- | ----------------- |
| POST   | `/api/payments/checkout`         | Inicia el pago con Stripe | Sí                |
| GET    | `/api/payments/order/{order_id}` | Ver pago de una orden     | Sí                |
| POST   | `/api/payments/webhook`          | Webhook de Stripe         | No (firma Stripe) |

### Servicios — `/api/services`

| Método | Endpoint                                    | Descripción                   | Auth  |
| ------ | ------------------------------------------- | ----------------------------- | ----- |
| GET    | `/api/services/store/{store_id}/categories` | Lista categorías de la tienda | No    |
| POST   | `/api/services/store/{store_id}/categories` | Crea una categoría            | Admin |
| PUT    | `/api/services/categories/{category_id}`    | Actualiza una categoría       | Admin |
| DELETE | `/api/services/categories/{category_id}`    | Desactiva una categoría       | Admin |
| GET    | `/api/services/store/{store_id}`            | Lista servicios de la tienda  | No    |
| GET    | `/api/services/category/{category_id}`      | Lista servicios por categoría | No    |
| GET    | `/api/services/{service_id}`                | Obtiene un servicio           | No    |
| POST   | `/api/services/store/{store_id}`            | Crea un servicio              | Admin |
| PUT    | `/api/services/{service_id}`                | Actualiza un servicio         | Admin |
| DELETE | `/api/services/{service_id}`                | Desactiva un servicio         | Admin |

### Citas — `/api/appointments`

| Método | Endpoint                                    | Descripción                  | Auth  |
| ------ | ------------------------------------------- | ---------------------------- | ----- |
| POST   | `/api/appointments/`                        | Agenda una cita              | Sí    |
| GET    | `/api/appointments/my`                      | Mis citas agendadas          | Sí    |
| GET    | `/api/appointments/store/{store_id}`        | Citas de la tienda           | Admin |
| GET    | `/api/appointments/{appointment_id}`        | Ver una cita                 | Sí    |
| PUT    | `/api/appointments/{appointment_id}`        | Modifica fecha/hora/notas    | Sí    |
| PATCH  | `/api/appointments/{appointment_id}/status` | Confirma, cancela o completa | Admin |
| DELETE | `/api/appointments/{appointment_id}`        | Cancela una cita             | Sí    |

### Dashboard — `/api/dashboard`

| Método | Endpoint                          | Descripción               | Auth       |
| ------ | --------------------------------- | ------------------------- | ---------- |
| GET    | `/api/dashboard/store/{store_id}` | Estadísticas de la tienda | Admin      |
| GET    | `/api/dashboard/superadmin`       | Estadísticas globales     | Superadmin |

### Panel Superadmin — `/api/admin`

| Método | Endpoint                              | Descripción                                      | Auth       |
| ------ | ------------------------------------- | ------------------------------------------------ | ---------- |
| GET    | `/api/admin/stores`                   | Lista todos los establecimientos                 | Superadmin |
| GET    | `/api/admin/stores/pending`           | Lista tiendas pendientes                         | Superadmin |
| PATCH  | `/api/admin/stores/{store_id}/status` | Aprueba o suspende tienda                        | Superadmin |
| GET    | `/api/admin/dashboard`                | Dashboard global                                 | Superadmin |
| GET    | `/api/admin/users`                    | Lista todos los usuarios (filtros: role, status) | Superadmin |
| GET    | `/api/admin/users/pending`            | Lista admins pendientes                          | Superadmin |
| GET    | `/api/admin/users/{user_id}`          | Obtiene un usuario por ID                        | Superadmin |
| POST   | `/api/admin/users`                    | Crea un usuario admin aprobado                   | Superadmin |
| PUT    | `/api/admin/users/{user_id}`          | Edita datos de un usuario                        | Superadmin |
| PATCH  | `/api/admin/users/{user_id}/status`   | Aprueba, suspende o activa usuario               | Superadmin |

---

## Autenticación

El sistema usa **JWT (JSON Web Tokens)** con el algoritmo HS256.

### Flujo de autenticación

1. El usuario se registra o hace login
2. El servidor genera un JWT firmado con la `SECRET_KEY`
3. El frontend guarda el token
4. En cada petición protegida el frontend envía el token en el header:
   ```
   Authorization: Bearer <token>
   ```
5. El servidor verifica la firma del token y extrae el `user_id`
6. Si el token es válido ejecuta el endpoint

### Validaciones en el login

El sistema verifica en orden:

1. Email y contraseña correctos
2. `is_active = True` — cuenta no eliminada
3. `status != suspended` — cuenta no suspendida
4. `status != pending` — cuenta aprobada por el superadmin

### Estructura del JWT

```json
{
  "sub": "1", // ID del usuario como string
  "exp": 1234567890 // Fecha de expiración en Unix timestamp
}
```

### Nota sobre contraseñas

Se usa **Argon2** en lugar de bcrypt por compatibilidad con Python 3.12.

---

## Comandos útiles

**Activar entorno virtual (Windows)**

```bash
venv\Scripts\activate
```

**Levantar servidor en modo desarrollo**

```bash
uvicorn app.main:app --reload
```

**Instalar una dependencia nueva**

```bash
pip install nombre-paquete
pip freeze > requirements.txt
```

**Generar migración**

```bash
alembic revision --autogenerate -m "descripcion"
```

**Aplicar migraciones**

```bash
alembic upgrade head
```

**Revertir última migración**

```bash
alembic downgrade -1
```

**Ver historial de migraciones**

```bash
alembic history
```

**Ver migración actual**

```bash
alembic current
```
