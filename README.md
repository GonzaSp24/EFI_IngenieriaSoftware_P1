# 🛫 Sistema de Gestión de Aerolínea - API REST

Sistema de gestión de aerolínea desarrollado con Django y Django Rest Framework, implementando el patrón Service-Repository con autenticación JWT y documentación Swagger.

---

## 📋 Tabla de Contenidos

- [Descripción del Proyecto](#-descripción-del-proyecto)
- [Características](#-características)
- [Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [Arquitectura](#-arquitectura)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [Endpoints de la API](#-endpoints-de-la-api)
- [Autenticación](#-autenticación)
- [Permisos](#-permisos)
- [Testing](#-testing)
- [Documentación Adicional](#-documentación-adicional)

---

## 📖 Descripción del Proyecto

Este proyecto se divide en dos partes:

### **Parte 1: Sistema Base Django**
Sistema de gestión de aerolínea con modelos para:
- ✈️ Vuelos y Aviones
- 👤 Pasajeros
- 🎫 Reservas y Boletos
- 💺 Asientos

### **Parte 2: API REST (Este Proyecto)**
Exposición de funcionalidades mediante API REST con:
- 🔐 Autenticación JWT
- 🛡️ Permisos basados en roles (Admin/Usuario)
- 📚 Documentación Swagger/ReDoc
- 🏗️ Arquitectura Service-Repository
- ✅ Validaciones robustas

---

## ✨ Características

### Funcionalidades Principales

#### 🔐 Autenticación y Autorización
- JWT (JSON Web Tokens) con refresh tokens
- Registro de usuarios
- Login/Logout
- Permisos diferenciados por rol

#### ✈️ Gestión de Vuelos
- CRUD completo de vuelos
- Búsqueda por origen/destino/fecha
- Consulta de asientos disponibles
- Solo Admin puede crear/modificar/eliminar

#### 👤 Gestión de Pasajeros
- CRUD completo de pasajeros
- Búsqueda por documento
- Validación de datos

#### 🎫 Gestión de Reservas
- Crear reservas (usuarios autenticados)
- Consultar reservas propias
- Cancelar reservas
- Validación de disponibilidad de asientos

#### 💺 Gestión de Asientos
- Consultar asientos por vuelo
- Ver disponibilidad
- Asignación automática en reservas

#### 📊 Reportes (Solo Admin)
- Vuelos con más reservas
- Pasajeros frecuentes
- Ocupación de vuelos
- Ingresos por vuelo

---

## 🛠️ Tecnologías Utilizadas

- **Python 3.10+**
- **Django 5.1.4** - Framework web
- **Django Rest Framework 3.15.2** - API REST
- **djangorestframework-simplejwt 5.4.0** - Autenticación JWT
- **drf-yasg 1.21.8** - Documentación Swagger
- **PostgreSQL** - Base de datos (producción)
- **SQLite** - Base de datos (desarrollo)
- **python-dotenv** - Variables de entorno

---

## 🏗️ Arquitectura

El proyecto sigue el patrón **Service-Repository** con separación clara de responsabilidades:

\`\`\`
┌─────────────────────────────────────────────────────────┐
│                    Cliente (HTTP)                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  ViewSets (API Layer)                    │
│  - Manejo de requests/responses                         │
│  - Validación de permisos                               │
│  - Serialización de datos                               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Services (Business Logic)                   │
│  - Lógica de negocio                                    │
│  - Validaciones complejas                               │
│  - Orquestación de operaciones                          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│           Repositories (Data Access Layer)               │
│  - Acceso a base de datos                               │
│  - Queries optimizadas                                  │
│  - Abstracción del ORM                                  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Models (Database)                       │
│  - Definición de tablas                                 │
│  - Relaciones entre entidades                           │
└─────────────────────────────────────────────────────────┘
\`\`\`

### Estructura de Carpetas

\`\`\`
aerolinea_project/
├── aerolinea_project/      # Configuración del proyecto
│   ├── settings.py         # Configuración principal
│   └── urls.py             # URLs principales
├── api/                    # App de API REST
│   ├── serializers/        # Transformación de datos
│   ├── repositories/       # Acceso a datos
│   ├── services/           # Lógica de negocio
│   ├── views/              # ViewSets (endpoints)
│   ├── permissions.py      # Permisos personalizados
│   └── urls.py             # Rutas de la API
├── vuelos/                 # App de vuelos
│   └── models.py           # Modelos: Vuelo, Avion, Asiento
├── pasajeros/              # App de pasajeros
│   └── models.py           # Modelo: Pasajero
├── reservas/               # App de reservas
│   └── models.py           # Modelos: Reserva, Boleto
└── core/                   # App principal
    └── management/         # Comandos personalizados
\`\`\`

---

## 🚀 Instalación

### Prerrequisitos

- Python 3.10 o superior
- pip (gestor de paquetes de Python)
- Git Bash (Windows) o Terminal (Linux/Mac)

### Pasos de Instalación

#### 1. Clonar el repositorio

\`\`\`bash
git clone <git@github.com:GonzaSp24/EFI_IngenieriaSoftware_P1.git>
cd EFI_IngenieriaSoftware_P1
\`\`\`

#### 2. Crear entorno virtual

**Windows (Git Bash):**
\`\`\`bash
python -m venv venv
source venv/Scripts/activate
\`\`\`

**Linux/Mac:**
\`\`\`bash
python3 -m venv venv
source venv/bin/activate
\`\`\`

#### 3. Instalar dependencias

\`\`\`bash
pip install -r requirements.txt
\`\`\`

#### 4. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

\`\`\`bash
cp .env.example .env
\`\`\`

Edita `.env` con tus configuraciones:

\`\`\`env
SECRET_KEY=tu-clave-secreta
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
\`\`\`

#### 5. Ejecutar migraciones

\`\`\`bash
python manage.py makemigrations
python manage.py migrate
\`\`\`

#### 6. Crear superusuario

\`\`\`bash
python manage.py createsuperuser
\`\`\`

Sigue las instrucciones para crear tu usuario administrador.

#### 7. (Opcional) Cargar datos de prueba

\`\`\`bash
python manage.py seed_data
\`\`\`

---

## ⚙️ Configuración

### Variables de Entorno

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `SECRET_KEY` | Clave secreta de Django | (requerido) |
| `DEBUG` | Modo debug | `True` |
| `ALLOWED_HOSTS` | Hosts permitidos | `localhost,127.0.0.1` |
| `DATABASE_URL` | URL de base de datos | `sqlite:///db.sqlite3` |

### Configuración de JWT

En `settings.py`:

\`\`\`python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}
\`\`\`

---

## 🎯 Uso

### Iniciar el servidor de desarrollo

\`\`\`bash
python manage.py runserver
\`\`\`

El servidor estará disponible en: `http://localhost:8000`

### Acceder a la documentación

- **Swagger UI**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/
- **Django Admin**: http://localhost:8000/admin/

### Ver todas las rutas disponibles

\`\`\`bash
python manage.py show_urls
\`\`\`

---

## 📡 Endpoints de la API

### Base URL
\`\`\`
http://localhost:8000/api/
\`\`\`

### Autenticación

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register/` | Registrar nuevo usuario | No |
| POST | `/api/auth/login/` | Iniciar sesión | No |
| POST | `/api/auth/logout/` | Cerrar sesión | Sí |
| POST | `/api/auth/token/refresh/` | Refrescar token | No |

### Vuelos

| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/vuelos/` | Listar vuelos | Público |
| POST | `/api/vuelos/` | Crear vuelo | Admin |
| GET | `/api/vuelos/{id}/` | Detalle de vuelo | Público |
| PUT | `/api/vuelos/{id}/` | Actualizar vuelo | Admin |
| DELETE | `/api/vuelos/{id}/` | Eliminar vuelo | Admin |
| GET | `/api/vuelos/buscar/` | Buscar vuelos | Público |
| GET | `/api/vuelos/{id}/asientos_disponibles/` | Ver asientos | Público |

### Pasajeros

| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/pasajeros/` | Listar pasajeros | Autenticado |
| POST | `/api/pasajeros/` | Crear pasajero | Autenticado |
| GET | `/api/pasajeros/{id}/` | Detalle de pasajero | Autenticado |
| PUT | `/api/pasajeros/{id}/` | Actualizar pasajero | Autenticado |
| DELETE | `/api/pasajeros/{id}/` | Eliminar pasajero | Admin |

### Reservas

| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/reservas/` | Listar reservas | Autenticado |
| POST | `/api/reservas/` | Crear reserva | Autenticado |
| GET | `/api/reservas/{id}/` | Detalle de reserva | Autenticado |
| POST | `/api/reservas/{id}/cancelar/` | Cancelar reserva | Autenticado |
| GET | `/api/reservas/mis_reservas/` | Mis reservas | Autenticado |

### Aviones

| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/aviones/` | Listar aviones | Público |
| POST | `/api/aviones/` | Crear avión | Admin |
| GET | `/api/aviones/{id}/` | Detalle de avión | Público |
| PUT | `/api/aviones/{id}/` | Actualizar avión | Admin |
| DELETE | `/api/aviones/{id}/` | Eliminar avión | Admin |

### Asientos

| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/asientos/` | Listar asientos | Público |
| GET | `/api/asientos/{id}/` | Detalle de asiento | Público |
| GET | `/api/asientos/por_vuelo/` | Asientos por vuelo | Público |

### Boletos

| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/boletos/` | Listar boletos | Autenticado |
| GET | `/api/boletos/{id}/` | Detalle de boleto | Autenticado |
| GET | `/api/boletos/mis_boletos/` | Mis boletos | Autenticado |

### Reportes (Solo Admin)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/reportes/vuelos_mas_reservados/` | Top vuelos |
| GET | `/api/reportes/pasajeros_frecuentes/` | Top pasajeros |
| GET | `/api/reportes/ocupacion_vuelos/` | Ocupación |
| GET | `/api/reportes/ingresos_por_vuelo/` | Ingresos |

---

## 🔐 Autenticación

### Registro de Usuario

\`\`\`bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "usuario",
    "email": "usuario@example.com",
    "password": "contraseña123",
    "password2": "contraseña123"
  }'
\`\`\`

### Login

\`\`\`bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "usuario",
    "password": "contraseña123"
  }'
\`\`\`

**Respuesta:**
\`\`\`json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "usuario",
    "email": "usuario@example.com"
  }
}
\`\`\`

### Usar el Token

Incluye el token en el header `Authorization`:

\`\`\`bash
curl -X GET http://localhost:8000/api/vuelos/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
\`\`\`

### Refrescar Token

\`\`\`bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }'
\`\`\`

---

## 🛡️ Permisos

### Roles de Usuario

#### Usuario Normal (Autenticado)
- ✅ Ver vuelos y aviones
- ✅ Crear y gestionar sus propios pasajeros
- ✅ Crear y ver sus propias reservas
- ✅ Ver sus propios boletos
- ❌ No puede crear/modificar vuelos
- ❌ No puede acceder a reportes

#### Administrador (Staff)
- ✅ Todas las funcionalidades de usuario normal
- ✅ Crear, modificar y eliminar vuelos
- ✅ Crear, modificar y eliminar aviones
- ✅ Ver todos los pasajeros y reservas
- ✅ Acceder a reportes del sistema

### Implementación de Permisos

\`\`\`python
# En api/permissions.py
class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
\`\`\`

---

## 🧪 Testing

### Ejecutar Tests

\`\`\`bash
# Todos los tests
python manage.py test

# Tests de una app específica
python manage.py test api

# Tests con verbosidad
python manage.py test --verbosity=2
\`\`\`

### Ejemplos de Pruebas con cURL

#### Crear un Vuelo (Admin)

\`\`\`bash
curl -X POST http://localhost:8000/api/vuelos/ \
  -H "Authorization: Bearer <tu-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "numero_vuelo": "AA123",
    "origen": "Buenos Aires",
    "destino": "Madrid",
    "fecha_salida": "2024-12-25T10:00:00Z",
    "fecha_llegada": "2024-12-25T22:00:00Z",
    "avion": 1,
    "precio": 850.00
  }'
\`\`\`

#### Buscar Vuelos

\`\`\`bash
curl -X GET "http://localhost:8000/api/vuelos/buscar/?origen=Buenos%20Aires&destino=Madrid&fecha=2024-12-25"
\`\`\`

#### Crear Reserva

\`\`\`bash
curl -X POST http://localhost:8000/api/reservas/ \
  -H "Authorization: Bearer <tu-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "vuelo": 1,
    "pasajero": 1,
    "asiento": 5
  }'
\`\`\`

---

## 📝 Comandos Útiles

\`\`\`bash
# Ver todas las rutas
python manage.py show_urls

# Cargar datos de prueba
python manage.py seed_data

# Crear superusuario
python manage.py createsuperuser

# Abrir shell de Django
python manage.py shell

# Verificar configuración
python manage.py check

# Recolectar archivos estáticos
python manage.py collectstatic
\`\`\`

---

## 👥 Contribución

Este proyecto fue desarrollado como parte del curso de Ingeniería de Software.

---

## 📄 Licencia

Este proyecto es de uso académico.

## 🎓 Créditos

Desarrollado como Parte 2 del proyecto de Ingeniería de Software - Sistema de Gestión de Aerolínea.

**Tecnologías principales:**
- Django & Django Rest Framework
- JWT Authentication
- Swagger/OpenAPI
- PostgreSQL/SQLite

---

**¡Gracias por usar el Sistema de Gestión de Aerolínea!** ✈️
