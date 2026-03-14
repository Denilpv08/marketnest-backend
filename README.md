# MarketNest Backend

API REST construida con **FastAPI** y **MySQL** para gestión de establecimientos y e-commerce multi-tenant. Permite a negocios crear su propia tienda online dentro de una plataforma centralizada.

---

## 📋 Tabla de contenidos

- [Descripción general](#descripción-general)
- [Stack tecnológico](#stack-tecnológico)
- [Arquitectura](#arquitectura)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Base de datos](#base-de-datos)
- [Roles del sistema](#roles-del-sistema)
- [Instalación y configuración](#instalación-y-configuración)
- [Migraciones](#migraciones)
- [Endpoints](#endpoints)
- [Autenticación](#autenticación)
- [Comandos útiles](#comandos-útiles)

---

## Descripción general

MarketNest es un SaaS (Software as a Service) multi-tenant donde:

- **Tú** (superadmin) controlas la plataforma — apruebas o rechazas solicitudes de establecimientos, gestionas suscripciones y monitoreas el sistema completo.
- **Los negocios** (admins) crean su tienda, suben productos, gestionan inventario, personalizan colores y logo, y ven estadísticas de ventas.
- **Los compradores** (customers) navegan tiendas, agregan productos al carrito y realizan compras con Stripe.

---

## Stack tecnológico

| Herramienta       | Versión | Propósito                               |
| ----------------- | ------- | --------------------------------------- |
| Python            | 3.12    | Lenguaje principal                      |
| FastAPI           | 0.111.0 | Framework web                           |
| Uvicorn           | 0.29.0  | Servidor ASGI                           |
| SQLAlchemy        | 2.0.30  | ORM — mapeo de modelos a tablas         |
| Alembic           | 1.13.1  | Migraciones de base de datos            |
| PyMySQL           | 1.1.1   | Driver de conexión a MySQL              |
| Pydantic          | 2.7.1   | Validación de datos de entrada y salida |
| pydantic-settings | 2.2.1   | Lectura de variables de entorno         |
| python-jose       | 3.3.0   | Generación y decodificación de JWT      |
| passlib + argon2  | 1.7.4   | Hasheo seguro de contraseñas            |
| Stripe            | 9.9.0   | Pasarela de pagos                       |
| python-dotenv     | 1.0.1   | Carga del archivo .env                  |

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
│   │   ├── user.py          # Tabla users + enum UserRole
│   │   ├── store.py         # Tabla stores + enum StoreStatus
│   │   ├── subscription.py  # Tabla store_subscriptions + enums de plan
│   │   ├── product.py       # Tabla products
│   │   ├── cart.py          # Tabla cart_items
│   │   ├── order.py         # Tablas orders + order_items + enum OrderStatus
│   │   └── payment.py       # Tabla payments + enum PaymentStatus
│   │
│   ├── schemas/             # Validación de datos con Pydantic
│   │   ├── __init__.py
│   │   ├── user.py          # UserCreate, UserLogin, UserResponse, TokenResponse
│   │   ├── store.py         # StoreCreate, StoreUpdate, StoreResponse
│   │   ├── product.py       # ProductCreate, ProductUpdate, ProductResponse
│   │   ├── cart.py          # CartItemCreate, CartItemUpdate, CartResponse
│   │   ├── order.py         # OrderResponse, OrderStatusUpdate
│   │   └── payment.py       # PaymentCreate, CheckoutResponse, PaymentResponse
│   │
│   ├── routers/             # Endpoints agrupados por dominio
│   │   ├── __init__.py
│   │   ├── auth.py          # /api/auth — registro, login, perfil
│   │   ├── stores.py        # /api/stores — gestión de tiendas
│   │   ├── products.py      # /api/products — productos e inventario
│   │   ├── cart.py          # /api/cart — carrito de compras
│   │   ├── orders.py        # /api/orders — órdenes de compra
│   │   ├── payments.py      # /api/payments — pagos con Stripe
│   │   ├── dashboard.py     # /api/dashboard — estadísticas
│   │   └── admin.py         # /api/admin — panel superadmin
│   │
│   ├── services/            # Lógica de negocio separada de los routers
│   │   ├── __init__.py
│   │   ├── auth_service.py       # Hasheo, JWT, registro, autenticación
│   │   ├── store_service.py      # CRUD de tiendas, aprobación
│   │   ├── product_service.py    # CRUD de productos, inventario
│   │   ├── cart_service.py       # Agregar, quitar, vaciar carrito
│   │   ├── order_service.py      # Crear orden desde carrito, estados
│   │   ├── payment_service.py    # Integración Stripe, webhooks
│   │   └── dashboard_service.py  # Estadísticas de tienda y sistema
│   │
│   └── middleware/          # Seguridad transversal
│       ├── auth.py          # Verificación JWT, control de roles
│       └── cors.py          # Configuración CORS para el frontend
│
├── alembic/                 # Sistema de migraciones
│   ├── env.py               # Configuración de Alembic — conecta con los modelos
│   ├── script.py.mako       # Plantilla para generar archivos de migración
│   └── versions/            # Archivos de migración generados
│
├── .env                     # Variables de entorno — NO subir a Git
├── .env.example             # Plantilla del .env — SÍ subir a Git
├── .gitignore               # Archivos excluidos del repositorio
├── alembic.ini              # Configuración base de Alembic
└── requirements.txt         # Dependencias del proyecto
```

---

## Base de datos

### Diagrama de tablas

```
users
├── id (PK)
├── name
├── email (unique)
├── password_hash
├── role: superadmin | admin | customer
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

### Relaciones entre tablas

- Un `User` puede tener una `Store` (si es admin)
- Una `Store` tiene un `Owner` (User con rol admin)
- Una `Store` tiene una `StoreSubscription`
- Una `Store` tiene muchos `Products`
- Una `Store` tiene muchas `Orders`
- Un `User` tiene muchos `CartItems`
- Un `User` tiene muchas `Orders`
- Una `Order` tiene muchos `OrderItems`
- Una `Order` tiene un `Payment`
- Un `Product` puede estar en muchos `CartItems` y `OrderItems`

---

## Roles del sistema

| Rol          | Descripción                 | Permisos                                                                                                |
| ------------ | --------------------------- | ------------------------------------------------------------------------------------------------------- |
| `superadmin` | Dueño del sistema           | Todo — ver y gestionar todos los establecimientos, aprobar/suspender tiendas, ver estadísticas globales |
| `admin`      | Dueño de un establecimiento | Gestionar su tienda, productos, inventario, ver sus órdenes y estadísticas                              |
| `customer`   | Comprador                   | Navegar tiendas, agregar al carrito, comprar                                                            |

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

Las migraciones son archivos que describen los cambios en la base de datos a lo largo del tiempo. Alembic compara los modelos de SQLAlchemy contra el estado actual de la BD y genera el SQL necesario automáticamente.

### Comandos principales

**Generar una migración nueva**

```bash
alembic revision --autogenerate -m "descripcion del cambio"
```

Úsalo cada vez que modifiques un modelo — agregues una columna, cambies un tipo de dato, etc.

**Aplicar migraciones pendientes**

```bash
alembic upgrade head
```

Aplica todas las migraciones que aún no se han ejecutado. `head` significa "hasta la más reciente".

**Revertir la última migración**

```bash
alembic downgrade -1
```

Deshace el último cambio aplicado. Útil cuando algo salió mal.

**Ver el historial de migraciones**

```bash
alembic history
```

Muestra todas las migraciones en orden cronológico.

**Ver la migración actual**

```bash
alembic current
```

Muestra en qué versión está la base de datos actualmente.

**Revertir todas las migraciones**

```bash
alembic downgrade base
```

Elimina todas las tablas creadas por Alembic. Úsalo con cuidado.

### Flujo de trabajo al modificar un modelo

1. Modifica el archivo del modelo en `app/models/`
2. Genera la migración: `alembic revision --autogenerate -m "agrega columna X a tabla Y"`
3. Revisa el archivo generado en `alembic/versions/`
4. Aplica la migración: `alembic upgrade head`

---

## Endpoints

### Autenticación — `/api/auth`

| Método | Endpoint             | Descripción                           | Auth requerida |
| ------ | -------------------- | ------------------------------------- | -------------- |
| POST   | `/api/auth/register` | Registra un nuevo usuario             | No             |
| POST   | `/api/auth/login`    | Inicia sesión con JSON                | No             |
| POST   | `/api/auth/token`    | Inicia sesión con form-data (Swagger) | No             |
| GET    | `/api/auth/me`       | Perfil del usuario autenticado        | Sí             |

### Tiendas — `/api/stores`

| Método | Endpoint                 | Descripción                        | Auth requerida |
| ------ | ------------------------ | ---------------------------------- | -------------- |
| POST   | `/api/stores/`           | Solicita crear una tienda          | Sí             |
| GET    | `/api/stores/`           | Lista mis tiendas                  | Sí             |
| GET    | `/api/stores/{slug}`     | Obtiene una tienda por slug        | No             |
| PUT    | `/api/stores/{store_id}` | Actualiza tienda y personalización | Admin          |

### Productos — `/api/products`

| Método | Endpoint                             | Descripción                | Auth requerida |
| ------ | ------------------------------------ | -------------------------- | -------------- |
| GET    | `/api/products/store/{store_id}`     | Lista productos activos    | No             |
| GET    | `/api/products/store/{store_id}/all` | Lista todos los productos  | Admin          |
| GET    | `/api/products/{product_id}`         | Obtiene un producto        | No             |
| POST   | `/api/products/store/{store_id}`     | Crea un producto           | Admin          |
| PUT    | `/api/products/{product_id}`         | Actualiza producto / stock | Admin          |
| DELETE | `/api/products/{product_id}`         | Desactiva un producto      | Admin          |

### Carrito — `/api/cart`

| Método | Endpoint              | Descripción                 | Auth requerida |
| ------ | --------------------- | --------------------------- | -------------- |
| GET    | `/api/cart/`          | Ver carrito con total       | Sí             |
| POST   | `/api/cart/`          | Agregar producto al carrito | Sí             |
| PUT    | `/api/cart/{item_id}` | Actualizar cantidad         | Sí             |
| DELETE | `/api/cart/{item_id}` | Eliminar ítem del carrito   | Sí             |
| DELETE | `/api/cart/`          | Vaciar todo el carrito      | Sí             |

### Órdenes — `/api/orders`

| Método | Endpoint                        | Descripción                  | Auth requerida |
| ------ | ------------------------------- | ---------------------------- | -------------- |
| POST   | `/api/orders/`                  | Crear orden desde el carrito | Sí             |
| GET    | `/api/orders/my`                | Historial de mis órdenes     | Sí             |
| GET    | `/api/orders/{order_id}`        | Ver una orden específica     | Sí             |
| GET    | `/api/orders/store/{store_id}`  | Órdenes de la tienda         | Admin          |
| PATCH  | `/api/orders/{order_id}/status` | Actualizar estado de orden   | Admin          |

### Pagos — `/api/payments`

| Método | Endpoint                         | Descripción               | Auth requerida    |
| ------ | -------------------------------- | ------------------------- | ----------------- |
| POST   | `/api/payments/checkout`         | Inicia el pago con Stripe | Sí                |
| GET    | `/api/payments/order/{order_id}` | Ver pago de una orden     | Sí                |
| POST   | `/api/payments/webhook`          | Webhook de Stripe         | No (firma Stripe) |

### Dashboard — `/api/dashboard`

| Método | Endpoint                          | Descripción               | Auth requerida |
| ------ | --------------------------------- | ------------------------- | -------------- |
| GET    | `/api/dashboard/store/{store_id}` | Estadísticas de la tienda | Admin          |
| GET    | `/api/dashboard/superadmin`       | Estadísticas globales     | Superadmin     |

### Panel Superadmin — `/api/admin`

| Método | Endpoint                              | Descripción                      | Auth requerida |
| ------ | ------------------------------------- | -------------------------------- | -------------- |
| GET    | `/api/admin/stores`                   | Lista todos los establecimientos | Superadmin     |
| GET    | `/api/admin/stores/pending`           | Lista tiendas pendientes         | Superadmin     |
| PATCH  | `/api/admin/stores/{store_id}/status` | Aprueba o suspende tienda        | Superadmin     |
| GET    | `/api/admin/dashboard`                | Dashboard global                 | Superadmin     |

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
6. Si el token es válido, ejecuta el endpoint

### Estructura del JWT

```json
{
  "sub": "1", // ID del usuario como string
  "exp": 1234567890 // Fecha de expiración en Unix timestamp
}
```

### Expiración

Los tokens expiran según `ACCESS_TOKEN_EXPIRE_MINUTES` del `.env` (por defecto 30 minutos). Cuando expira el usuario debe hacer login de nuevo.

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

**Levantar servidor en un puerto específico**

```bash
uvicorn app.main:app --reload --port 8001
```

**Instalar una dependencia nueva**

```bash
pip install nombre-paquete
pip freeze > requirements.txt  # Actualizar requirements.txt
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
