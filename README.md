
# 🛫 Sistema de Gestión de Aerolínea — API REST

API REST desarrollada en **Django Rest Framework (DRF)** para la gestión integral de una aerolínea.  
Permite administrar vuelos, pasajeros, reservas, boletos y autenticación mediante **JWT**, siguiendo el **patrón Service–Repository**.

---

## 📋 Descripción General

Esta API ofrece funcionalidades completas para:

- Gestión de vuelos, aviones y asientos  
- Registro y administración de pasajeros  
- Sistema de reservas (creación, confirmación, cancelación)  
- Generación de boletos electrónicos  
- Autenticación segura con **JWT**  
- Documentación interactiva con **Swagger** y **ReDoc**

---

## 🧱 Arquitectura

El sistema implementa una arquitectura en capas que promueve la separación de responsabilidades y la mantenibilidad:

```
┌─────────────────────────────────────────┐
│ Views (API Endpoints)                   │ ← Recibe peticiones HTTP
├─────────────────────────────────────────┤
│ Serializers (Validación)                │ ← Valida y serializa datos
├─────────────────────────────────────────┤
│ Services (Lógica de Negocio)            │ ← Implementa reglas de negocio
├─────────────────────────────────────────┤
│ Repositories (Acceso a Datos)           │ ← Consultas a la base de datos
├─────────────────────────────────────────┤
│ Models (Base de Datos)                  │ ← Modelos de Django
└─────────────────────────────────────────┘
```

### ✅ Ventajas
- **Separación de responsabilidades**
- **Reutilización de código**
- **Facilidad de testing**
- **Alta mantenibilidad**

---

## 🔐 Autenticación (JWT)

### Obtener Tokens
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "usuario",
  "password": "contraseña"
}
```

**Respuesta:**
```json
{
  "error": false,
  "message": "Login exitoso",
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "id": 1,
      "username": "usuario",
      "email": "usuario@example.com"
    }
  }
}
```

### Uso del Token
```http
Authorization: Bearer {access_token}
```

### Endpoints de Autenticación

| Método | Endpoint | Descripción |
|--------|-----------|-------------|
| POST | `/api/auth/register/` | Registro de usuario |
| POST | `/api/auth/login/` | Inicio de sesión |
| POST | `/api/auth/logout/` | Cierre de sesión |
| POST | `/api/auth/token/refresh/` | Renovar token |

---

## 🧭 Endpoints Principales

| Recurso | Endpoints Ejemplo |
|----------|------------------|
| **Vuelos** | `/api/vuelos/`, `/api/vuelos/{id}/`, `/api/vuelos/buscar/` |
| **Pasajeros** | `/api/pasajeros/`, `/api/pasajeros/{id}/` |
| **Reservas** | `/api/reservas/`, `/api/reservas/{id}/`, `/api/reservas/mis_reservas/` |
| **Aviones** | `/api/aviones/`, `/api/aviones/{id}/` |
| **Asientos** | `/api/asientos/por_vuelo/?vuelo_id={id}` |
| **Boletos** | `/api/boletos/`, `/api/boletos/{id}/` |
| **Reportes** | `/api/reportes/vuelos_mas_reservados/`, `/api/reportes/pasajeros_frecuentes/` |

---

## ✈️ Funcionalidades Principales

### Vuelos
- Listar todos los vuelos disponibles  
- Obtener detalle de un vuelo  
- Filtrar por origen, destino y fecha  
- Crear, editar y eliminar vuelos (solo administradores)

### Pasajeros
- Registrar pasajeros  
- Consultar información de un pasajero  
- Listar reservas asociadas

### Reservas
- Crear reservas para pasajeros  
- Seleccionar asiento disponible  
- Confirmar o cancelar reservas  

### Aviones y Asientos
- Listar aviones registrados  
- Obtener layout de asientos  
- Verificar disponibilidad  

### Boletos
- Generar boleto desde una reserva confirmada  
- Consultar boleto por código  

### Reportes
- Pasajeros por vuelo  
- Reservas activas por pasajero  
- Vuelos más reservados  

---

## ⚙️ Requisitos Técnicos

- **Python 3.10+**  
- **Django 5.x**  
- **Django Rest Framework 3.15.x**  
- **SimpleJWT** (autenticación JWT)  
- **drf-yasg** (Swagger / ReDoc)  
- **SQLite o PostgreSQL**

---

## 🚀 Instalación y Uso

```bash
# Clonar repositorio
git clone git@github.com:GonzaSp24/EFI_IngenieriaSoftware_P1.git
cd EFI_IngenieriaSoftware_P1

# Crear entorno virtual
python -m venv venv
source venv/bin/activate   # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Migraciones y superusuario
python manage.py migrate
python manage.py createsuperuser

# Ejecutar servidor
python manage.py runserver
```

### Accesos principales
- **API Root:** [http://localhost:8000/api/](http://localhost:8000/api/)   
- **ReDoc:** [http://localhost:8000/api/redoc/](http://localhost:8000/api/redoc/)  
- **Admin:** [http://localhost:8000/api/admin/](http://localhost:8000/api/admin/)

---

## 🔑 Permisos y Roles

| Rol | Permisos |
|------|-----------|
| **Público** | Registro y login |
| **Autenticado** | Consultar vuelos, crear reservas propias |
| **Propietario** | Ver y modificar sus propias reservas y boletos |
| **Admin** | Acceso total a todos los recursos |

---

## 📦 Formato de Respuestas

### Éxito
```json
{
  "error": false,
  "message": "Operación exitosa",
  "data": {...}
}
```

### Error
```json
{
  "error": true,
  "message": "Descripción del error",
  "details": {...}
}
```

---

## ⚙️ Códigos de Estado HTTP

| Código | Descripción |
|--------|--------------|
| 200 | OK — Operación exitosa |
| 201 | Created — Recurso creado |
| 400 | Bad Request — Datos inválidos |
| 401 | Unauthorized — No autenticado |
| 403 | Forbidden — Sin permisos |
| 404 | Not Found — Recurso no encontrado |
| 500 | Internal Server Error — Error del servidor |

---

## 📚 Documentación Interactiva

- **Swagger UI:** [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)  
- **ReDoc:** [http://localhost:8000/api/redoc/](http://localhost:8000/api/redoc/)

Desde Swagger puedes probar los endpoints directamente desde el navegador.

---

## 👨‍💻 Autores

- **Pablo Aldo Amedey Dilena**  
- **Gonzalo Spernanzoni**
