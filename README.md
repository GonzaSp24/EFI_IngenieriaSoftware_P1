# 🛫 Sistema de Gestión de Aerolínea — API REST

Proyecto desarrollado en **Django Rest Framework (DRF)** como extensión de la Parte 1 del sistema de gestión de aerolínea. Expone las funcionalidades del sistema mediante una **API REST segura, documentada y basada en roles**, siguiendo el **patrón Service–Repository**.

---

## 🎯 Objetivo

Permitir a la aerolínea ofrecer acceso a terceros (aplicaciones móviles o portales externos) a través de una API REST documentada, segura y consistente.

---

## ⚙️ Requisitos Técnicos Cumplidos

- Django Rest Framework (DRF)
- Patrón **Service–Repository**
- Serializers para conversión de modelos a JSON
- Vistas basadas en **ViewSets**
- Ruteo de endpoints con `urls.py`
- Documentación **Swagger/ReDoc**
- Autenticación **JWT** (login, refresh, logout)
- Permisos y roles de usuario (admin / usuario)

---

## ✈️ Funcionalidades Principales

### **Gestión de Vuelos (API)**
- Listar todos los vuelos disponibles.
- Obtener detalle de un vuelo.
- Filtrar por origen, destino y fecha.
- Crear, editar y eliminar vuelos (solo administradores).

### **Gestión de Pasajeros (API)**
- Registrar pasajeros.
- Consultar información de un pasajero.
- Listar reservas asociadas a un pasajero.

### **Sistema de Reservas (API)**
- Crear reservas para pasajeros en vuelos.
- Seleccionar asiento disponible.
- Confirmar o cancelar reservas.

### **Gestión de Aviones y Asientos (API)**
- Listar aviones registrados.
- Obtener layout de asientos de un avión.
- Verificar disponibilidad de asientos.

### **Boletos (API)**
- Generar boleto a partir de una reserva confirmada.
- Consultar boleto por código.

### **Reportes (API)**
- Listado de pasajeros por vuelo.
- Reservas activas por pasajero.

---

## 🧱 Tecnologías Utilizadas

- **Python 3.10+**
- **Django 5.x**
- **Django Rest Framework 3.15.x**
- **SimpleJWT** (autenticación JWT)
- **drf-yasg** (documentación Swagger)
- **SQLite / PostgreSQL** (según entorno)

---

## 🚀 Instalación y Uso Rápido

```bash
# Clonar repositorio
git clone git@github.com:GonzaSp24/EFI_IngenieriaSoftware_P1.git
cd EFI_IngenieriaSoftware_P1

# Crear entorno virtual y activar
python -m venv venv
source venv/bin/activate  # En Windows: source venv/Scripts/activate

# Instalar dependencias
pip install -r requirements.txt

# Migraciones y superusuario
python manage.py migrate
python manage.py createsuperuser

# Ejecutar servidor
python manage.py runserver
```

**Accesos principales:**
- API Root → `http://localhost:8000/api/`
- Swagger → `http://localhost:8000/swagger/`
- ReDoc → `http://localhost:8000/redoc/`
- Admin → `http://localhost:8000/admin/`

---

## 🔐 Autenticación (JWT)

Endpoints principales:
| Método | Endpoint | Descripción |
|--------|-----------|-------------|
| POST | `/api/auth/register/` | Registro de usuario |
| POST | `/api/auth/login/` | Inicio de sesión |
| POST | `/api/auth/logout/` | Cierre de sesión |
| POST | `/api/auth/token/refresh/` | Renovar token |

---

## 🧭 Endpoints Principales

| Recurso | Ejemplos de Endpoints |
|----------|----------------------|
| **Vuelos** | `/api/vuelos/`, `/api/vuelos/{id}/`, `/api/vuelos/buscar/` |
| **Pasajeros** | `/api/pasajeros/`, `/api/pasajeros/{id}/` |
| **Reservas** | `/api/reservas/`, `/api/reservas/{id}/`, `/api/reservas/mis_reservas/` |
| **Aviones** | `/api/aviones/`, `/api/aviones/{id}/` |
| **Asientos** | `/api/asientos/por_vuelo/?vuelo_id={id}` |
| **Boletos** | `/api/boletos/`, `/api/boletos/{id}/` |
| **Reportes** | `/api/reportes/vuelos_mas_reservados/`, `/api/reportes/pasajeros_frecuentes/` |

---

## 📚 Documentación

- API Documentada con **Swagger y ReDoc**
- Patrón **Service–Repository** aplicado en capas `services/` y `repositories/`
- Validaciones en serializers y servicios
- Manejo de errores con respuestas HTTP adecuadas (400, 401, 404, 500)

---

## 👨‍💻 Autores

**Amedey Dilena Pablo Aldo**  
**Spernanzoni Gonzalo**  

---
