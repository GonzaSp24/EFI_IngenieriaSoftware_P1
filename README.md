# Sistema de Gestión de Aerolínea (AeroSystem)

Sistema web completo para gestionar una aerolínea, desarrollado con Django.

## 🚀 Características

### Funcionalidades Principales
- **Gestión de Vuelos**: Crear, editar, eliminar y visualizar vuelos (en Admin y Web).
- **Gestión de Pasajeros**: Registro, listado y visualización de historial de vuelos.
- **Sistema de Reservas**: Visualización de disponibilidad de asientos, reserva de asientos específicos, gestión de estados y generación de boletos electrónicos.
- **Gestión de Aviones**: Registro de flota, definición de layout de asientos (automático al crear avión) y mantenimiento de información técnica.
- **Reportes**: Listado de pasajeros por vuelo.
- **Autenticación de Usuarios**: Registro, inicio y cierre de sesión con roles (Administrador, Empleado, Cliente).

### Características Técnicas
- Desarrollado con **Django 4.2**.
- Base de datos **SQLite** (fácilmente configurable para PostgreSQL).
- Interfaz de usuario amigable y responsive con **Bootstrap 5** (solo CSS, sin JS personalizado).
- Iconos de **Font Awesome**.
- Manejo de relaciones entre modelos.
- Validaciones en el backend y frontend (a través de formularios de Django).
- Manejo de mensajes de éxito/error.
- Paginación para listas largas.

## 🛠️ Instalación y Configuración

### Requisitos Previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1.  **Clonar el repositorio** (o si ya lo tienes, asegúrate de estar en la raíz del proyecto `SistemaGestionAvionesDeepSekk`):
    \`\`\`bash
    git clone <url-del-repositorio>
    cd SistemaGestionAvionesDeepSekk
    \`\`\`

2.  **Crear y activar el entorno virtual**:
    \`\`\`bash
    python3 -m venv venv
    # En Linux/macOS:
    source venv/bin/activate
    # En Windows (CMD):
    venv\Scripts\activate.bat
    # En Windows (PowerShell):
    .\venv\Scripts\Activate.ps1
    \`\`\`

3.  **Instalar dependencias**:
    \`\`\`bash
    pip install -r requirements.txt
    \`\`\`

4.  **Configurar la base de datos y aplicar migraciones**:
    Es crucial que las tablas se creen correctamente. Si ya intentaste migraciones antes y tuviste errores, es recomendable limpiar la base de datos y las migraciones anteriores.

    **Opción A: Script de limpieza y configuración (Recomendado)**
    Este script eliminará la base de datos `db.sqlite3` y las migraciones anteriores, luego creará nuevas migraciones, las aplicará y creará un superusuario `admin` con contraseña `admin123`.
    \`\`\`bash
    # En Linux/macOS:
    chmod +x scripts/fix_database.sh
    ./scripts/fix_database.sh

    # En Windows, ejecuta los comandos dentro del script manualmente en tu terminal:
    # del db.sqlite3
    # find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
    # find . -path "*/migrations/*.pyc" -delete
    # python manage.py makemigrations usuarios core vuelos pasajeros reservas
    # python manage.py migrate
    # python manage.py shell -c "from django.contrib.auth.models import User; if not User.objects.filter(username='admin').exists(): User.objects.create_superuser('admin', 'admin@example.com', 'admin123'); print('✅ Superusuario creado: admin/admin123')"
    \`\`\`

    **Opción B: Comandos manuales (si prefieres control total)**
    \`\`\`bash
    # 1. Eliminar base de datos existente (si hay problemas)
    rm db.sqlite3  # En Windows: del db.sqlite3

    # 2. Eliminar archivos de migración anteriores (EXCEPTO __init__.py)
    # En Linux/macOS:
    find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
    # En Windows, navega a cada carpeta de app (usuarios, core, vuelos, pasajeros, reservas)
    # y elimina manualmente los archivos .py (ej. 0001_initial.py) dentro de la carpeta 'migrations'.

    # 3. Crear nuevas migraciones para todas las apps
    python manage.py makemigrations usuarios core vuelos pasajeros reservas

    # 4. Aplicar todas las migraciones a la base de datos
    python manage.py migrate

    # 5. Crear un superusuario (administrador)
    python manage.py createsuperuser
    # Sigue las instrucciones para crear tu nombre de usuario, email y contraseña.
    # Sugerencia: usuario 'admin', contraseña 'admin123'
    \`\`\`

5.  **Cargar datos de ejemplo (opcional pero recomendado)**:
    Esto poblará tu base de datos con algunos aviones, vuelos, pasajeros y reservas para que puedas probar el sistema de inmediato.
    \`\`\`bash
    python scripts/setup_database_fixed.py
    \`\`\`

6.  **Ejecutar el servidor de desarrollo**:
    \`\`\`bash
    python manage.py runserver
    \`\`\`

7.  **Acceder a la aplicación**:
    -   Aplicación web: [http://localhost:8000/](http://localhost:8000/)
    -   Panel de administración: [http://localhost:8000/admin/](http://localhost:8000/admin/)

## 👨‍💻 Uso del Sistema

### Credenciales por Defecto
Si ejecutaste el script de datos de ejemplo o `createsuperuser`:
-   **Usuario administrador**: `admin`
-   **Contraseña**: `admin123` (o la que hayas definido)

### Flujo de Trabajo Típico

1.  **Configuración Inicial (Panel Admin)**:
    *   Accede a [http://localhost:8000/admin/](http://localhost:8000/admin/) con tus credenciales de superusuario.
    *   En la sección "Gestión de Vuelos", ve a "Aviones" y crea algunos aviones. Al guardar un nuevo avión, sus asientos se generarán automáticamente según la capacidad, filas y columnas definidas.
    *   Luego, en "Vuelos", crea vuelos asignando los aviones, rutas, fechas y precios. Estos vuelos aparecerán automáticamente en la web pública.

2.  **Registro de Pasajeros (Web o Admin)**:
    *   Desde la web, puedes ir a "Pasajeros" -> "Nuevo Pasajero" para registrar nuevos viajeros.
    *   También puedes gestionarlos desde el panel de administración.

3.  **Proceso de Reserva (Web)**:
    *   En la página de inicio o en "Vuelos", busca vuelos por origen, destino y fecha.
    *   Haz clic en "Ver Detalles" de un vuelo para ver su mapa de asientos.
    *   Selecciona un asiento disponible (verde).
    *   En la página de confirmación de reserva, elige un pasajero existente (o registra uno nuevo si es necesario).
    *   Confirma la reserva. Se generará automáticamente un código de reserva y un boleto electrónico.

4.  **Gestión de Reservas (Web)**:
    *   Ve a "Mis Reservas" para ver todas las reservas confirmadas.
    *   Desde allí, puedes ver los detalles de cada reserva, el boleto electrónico y la opción de cancelar la reserva.

5.  **Reportes (Web)**:
    *   Desde el detalle de un vuelo, puedes acceder al "Reporte de Pasajeros" para ver un listado de todos los pasajeros confirmados para ese vuelo.

## 📂 Estructura del Proyecto

\`\`\`
SistemaGestionAvionesDeepSekk/
├── aerolinea_project/          # Configuración principal del proyecto
│   ├── __init__.py
│   ├── settings.py             # Configuraciones generales
│   ├── urls.py                 # URLs principales del proyecto
│   └── wsgi.py
├── core/                       # Aplicación para funcionalidades base (ej. página de inicio)
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── pasajeros/                  # Aplicación para la gestión de pasajeros
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   └── urls.py
│   └── views.py
├── reservas/                   # Aplicación para el sistema de reservas y boletos
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   └── urls.py
│   └── views.py
├── scripts/                    # Scripts de utilidad
│   ├── fix_database.sh         # Script para limpiar y configurar la BD
│   └── setup_database_fixed.py # Script para cargar datos de ejemplo
├── static/                     # Archivos estáticos globales (si los añades)
├── templates/                  # Plantillas HTML de todo el proyecto
│   ├── base.html               # Plantilla base con Bootstrap y Font Awesome
│   ├── core/
│   │   └── home.html
│   ├── pasajeros/
│   │   ├── detalle_pasajero.html
│   │   ├── historial_vuelos_pasajero.html
│   │   ├── lista_pasajeros.html
│   │   └── registrar_pasajero.html
│   ├── registration/           # Plantillas de autenticación de Django
│   │   ├── login.html
│   │   └── registro.html
│   ├── reservas/
│   │   ├── boleto_electronico.html
│   │   ├── cancelar_reserva.html
│   │   ├── crear_reserva.html
│   │   ├── detalle_reserva.html
│   │   └── mis_reservas.html
│   └── vuelos/
│       ├── detalle_vuelo.html
│       ├── lista_vuelos.html
│       └── reporte_pasajeros_vuelo.html
├── usuarios/                   # Aplicación para el modelo de usuario personalizado
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   └── urls.py
│   └── views.py
├── vuelos/                     # Aplicación para la gestión de aviones y vuelos
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   └── urls.py
│   └── views.py
├── db.sqlite3                  # Archivo de base de datos SQLite (generado)
├── manage.py                   # Utilidad de línea de comandos de Django
└── requirements.txt            # Dependencias del proyecto
\`\`\`

## 📝 Consideraciones Adicionales

-   **Validaciones**: Se han implementado validaciones básicas en los modelos y formularios de Django.
-   **Manejo de Errores**: Los mensajes de error y éxito se muestran al usuario a través del sistema de mensajes de Django.
-   **Documentación**: El código incluye comentarios para facilitar su comprensión.
-   **Pruebas Unitarias**: (Opcional) Puedes añadir tus pruebas en los archivos `tests.py` de cada aplicación.
-   **Buenas Prácticas**: Se sigue la estructura de aplicaciones de Django y se utilizan sus funcionalidades integradas.

Espero que esta solución te sea de gran ayuda para tu evaluación final. ¡Mucho éxito!
