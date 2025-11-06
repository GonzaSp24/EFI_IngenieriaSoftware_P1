import os
import django
from django.core.exceptions import ImproperlyConfigured

# ============================================================
# 🧩 CONFIGURACIÓN INICIAL
# ============================================================

import sys
import os

# Asegura que el directorio raíz del proyecto esté en sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aerolinea_project.settings")

try:
    django.setup()
    print("✅ Django configurado correctamente")
except ImproperlyConfigured as e:
    print(f"❌ Error configurando Django: {e}")
    exit(1)


# ============================================================
# 📦 IMPORTAR MODELOS
# ============================================================

try:
    from airline.models import (
        Avion, Vuelo, Asiento, Reserva, Boleto, Pasajero
    )
    from django.contrib.auth.models import User
    print("✅ Modelos importados correctamente")
except Exception as e:
    print(f"❌ Error importando modelos: {e}")
    exit(1)


# ============================================================
# 🔍 FUNCIONES DE VERIFICACIÓN
# ============================================================

def verificar_migraciones():
    """Verifica que todas las migraciones estén aplicadas."""
    from django.db import connections, DEFAULT_DB_ALIAS
    from django.db.migrations.executor import MigrationExecutor

    print("🔍 Verificando migraciones pendientes...")
    try:
        connection = connections[DEFAULT_DB_ALIAS]
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())

        if plan:
            print("❌ Hay migraciones pendientes:")
            for migration in plan:
                app_label, migration_name = migration[0]
                print(f"   - {app_label}.{migration_name}")
            print("⚠️  Ejecuta primero: python manage.py migrate")
            return False

        print("✅ Todas las migraciones están aplicadas correctamente")
        return True

    except Exception as e:
        print(f"❌ Error verificando migraciones: {e}")
        return False


def verificar_tablas():
    """Verifica que existan las tablas necesarias en la base de datos."""
    from django.db import connection
    print("🔍 Verificando tablas en la base de datos...")

    try:
        tablas = connection.introspection.table_names()
        requeridas = [
            Avion._meta.db_table,
            Vuelo._meta.db_table,
            Asiento._meta.db_table,
            Reserva._meta.db_table,
            Boleto._meta.db_table,
            Pasajero._meta.db_table,
        ]
        faltantes = [t for t in requeridas if t not in tablas]

        if faltantes:
            print("❌ Tablas faltantes:")
            for t in faltantes:
                print(f"   - {t}")
            print("⚠️  Ejecuta: python manage.py migrate")
            return False

        print("✅ Todas las tablas necesarias existen")
        return True

    except Exception as e:
        print(f"❌ Error verificando tablas: {e}")
        return False


# ============================================================
# 💾 CARGA DE DATOS DE EJEMPLO
# ============================================================

def cargar_datos_ejemplo():
    """Crea datos de ejemplo si la base está vacía."""
    from datetime import datetime, timedelta

    if Avion.objects.exists():
        print("ℹ️  Ya existen datos en la base. No se cargan ejemplos.")
        return

    print("✈️  Creando datos de ejemplo...")

    aviones = [
        Avion.objects.create(modelo="Boeing 737", filas=30, columnas=6),
        Avion.objects.create(modelo="Airbus A320", filas=35, columnas=6),
        Avion.objects.create(modelo="Boeing 777", filas=40, columnas=10),
    ]
    
    vuelos = []
    for i, avion in enumerate(aviones):
        vuelo = Vuelo.objects.create(
        origen="Buenos Aires",
        destino=["Córdoba", "Mendoza", "Rosario"][i],
        fecha_salida=datetime.now() + timedelta(days=i+1),
        fecha_llegada=datetime.now() + timedelta(days=i+1, hours=2),
        duracion=timedelta(hours=2),
        estado='programado',
        precio_base=5000 + (i*1000),
        avion=avion
    )
    vuelos.append(vuelo)

    
    pasajero = Pasajero.objects.create(
        nombre="Juan",
        apellido="Pérez",
        tipo_documento="DNI",
        documento="12345678",
        email="juan@example.com",
        telefono="+5491123456789",
        fecha_nacimiento="1990-05-15"
    )

    print("✅ Datos de ejemplo creados correctamente")
    print(f"   - {len(aviones)} aviones creados")
    print(f"   - {len(vuelos)} vuelos creados")
    print(f"   - {Pasajero.objects.count()} pasajeros creados")


# ============================================================
# 🚀 EJECUCIÓN PRINCIPAL
# ============================================================

def main():
    print("\n🚀 Iniciando configuración de base de datos...\n")

    if not verificar_migraciones():
        exit(1)

    if not verificar_tablas():
        exit(1)

    cargar_datos_ejemplo()

    print("\n🎉 CONFIGURACIÓN COMPLETADA CON ÉXITO\n")


if __name__ == "__main__":
    main()
