"""
Script para configurar la base de datos con datos de ejemplo
"""

import os
import sys
import django
from datetime import datetime, timedelta, date
from decimal import Decimal

# Configuración de Django
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aerolinea_project.settings')

try:
    django.setup()
    print("✅ Django configurado correctamente")
except Exception as e:
    print(f"❌ Error configurando Django: {e}")
    sys.exit(1)

# Importación de modelos (corregido para evitar importaciones circulares)
try:
    from vuelos.models import Avion, Vuelo, Asiento
    from pasajeros.models import Pasajero
    from reservas.models import Reserva, Boleto
    from usuarios.models import CustomUser
    print("✅ Modelos importados correctamente")
except ImportError as e:
    print(f"❌ Error importando modelos: {e}")
    sys.exit(1)

def crear_asientos_para_avion(avion):
    print(f"✈️ Generando asientos para: {avion.modelo}")

    for fila in range(1, avion.filas + 1):
        for col_idx in range(avion.columnas):
            columna = chr(65 + col_idx)  # Letras A, B, C, ...
            numero = f"{fila}{columna}"

            tipo = (
                'primera' if fila <= 3 else
                'ejecutiva' if fila <= 10 else
                'economica'
            )

            asiento, created = Asiento.objects.get_or_create(
                avion=avion,
                numero=numero,
                defaults={
                    'fila': fila,
                    'columna': columna,
                    'tipo': tipo,
                    'estado': 'disponible'
                }
            )
            if created:
                print(f"  ➕ Creado asiento {numero}")
            else:
                print(f"  ✅ Ya existe asiento {numero}")

def crear_datos_ejemplo():
    print("\n🚀 Iniciando creación de datos de ejemplo...\n")
    
    # Usuarios
    if not CustomUser.objects.filter(username='admin').exists():
        CustomUser.objects.create_superuser('admin', 'admin@aerolinea.com', 'admin123', rol='admin')
        print("✅ Superusuario creado: admin/admin123")

    usuarios = [
        {'username': 'empleado1', 'email': 'empleado@aerolinea.com', 'password': 'emp123', 'rol': 'empleado'},
        {'username': 'cliente1', 'email': 'cliente@email.com', 'password': 'cli123', 'rol': 'cliente'}
    ]
    for u in usuarios:
        if not CustomUser.objects.filter(username=u['username']).exists():
            CustomUser.objects.create_user(**u)
            print(f"✅ Usuario creado: {u['username']}")

    # Aviones
    aviones_data = [
        {'modelo': 'Boeing 737-800', 'capacidad': 189, 'filas': 32, 'columnas': 6},
        {'modelo': 'Airbus A320', 'capacidad': 180, 'filas': 30, 'columnas': 6},
        {'modelo': 'Embraer E190', 'capacidad': 114, 'filas': 19, 'columnas': 6},
    ]
    aviones = []
    for data in aviones_data:
        avion, created = Avion.objects.get_or_create(modelo=data['modelo'], defaults=data)
        aviones.append(avion)
        if created:
            crear_asientos_para_avion(avion)
            print(f"✅ Avión creado: {avion.modelo}")
        else:
            if avion.asiento_set.count() == 0:
                crear_asientos_para_avion(avion)

    # Vuelos
    base_date = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
    vuelos_data = [
        {
            'avion': aviones[0], 'origen': 'Buenos Aires', 'destino': 'Córdoba',
            'fecha_salida': base_date + timedelta(days=1), 'duracion': timedelta(hours=1, minutes=30),
            'precio_base': Decimal('25000.00'), 'estado': 'programado'
        },
        {
            'avion': aviones[1], 'origen': 'Buenos Aires', 'destino': 'Mendoza',
            'fecha_salida': base_date + timedelta(days=2), 'duracion': timedelta(hours=2),
            'precio_base': Decimal('30000.00'), 'estado': 'programado'
        },
    ]
    vuelos = []
    for v in vuelos_data:
        v['fecha_llegada'] = v['fecha_salida'] + v['duracion']
        vuelo, created = Vuelo.objects.get_or_create(
            avion=v['avion'], origen=v['origen'], destino=v['destino'], fecha_salida=v['fecha_salida'],
            defaults=v
        )
        vuelos.append(vuelo)
        if created:
            print(f"✅ Vuelo creado: {vuelo}")

    # Pasajeros
    pasajeros_data = [
        {
            'nombre': 'Juan Carlos', 'apellido': 'Pérez', 'tipo_documento': 'DNI',
            'documento': '12345678', 'email': 'juan.perez@email.com',
            'telefono': '+54 11 1234-5678', 'fecha_nacimiento': date(1985, 5, 15)
        },
        {
            'nombre': 'María Elena', 'apellido': 'González', 'tipo_documento': 'DNI',
            'documento': '87654321', 'email': 'maria.gonzalez@email.com',
            'telefono': '+54 11 8765-4321', 'fecha_nacimiento': date(1990, 8, 22)
        },
    ]
    pasajeros = []
    for p in pasajeros_data:
        pasajero, _ = Pasajero.objects.get_or_create(documento=p['documento'], defaults=p)
        pasajeros.append(pasajero)
        print(f"✅ Pasajero creado: {pasajero}")

    # Reservas
    for i in range(min(len(pasajeros), len(vuelos))):
        vuelo = vuelos[i]
        pasajero = pasajeros[i]
        asiento = vuelo.avion.asiento_set.filter(estado='disponible').first()

        if asiento:
            reserva = Reserva.objects.create(
                vuelo=vuelo,
                pasajero=pasajero,
                asiento=asiento,
                precio=vuelo.precio_base,
                estado='confirmada'
            )
            asiento.estado = 'ocupado'
            asiento.save()
            Boleto.objects.create(reserva=reserva)
            print(f"🎟️  Reserva creada: {reserva.codigo_reserva} para {pasajero.nombre}")
        else:
            print(f"⚠️  No hay asientos disponibles para el vuelo {vuelo}")

    # Resumen
    print("\n📊 Resumen:")
    print(f"   • Usuarios: {CustomUser.objects.count()}")
    print(f"   • Aviones: {Avion.objects.count()}")
    print(f"   • Asientos: {Asiento.objects.count()}")
    print(f"   • Vuelos: {Vuelo.objects.count()}")
    print(f"   • Pasajeros: {Pasajero.objects.count()}")
    print(f"   • Reservas: {Reserva.objects.count()}")
    print(f"   • Boletos: {Boleto.objects.count()}")

    print("\n🔑 Acceso:")
    print("   Admin: admin / admin123")
    print("   Web: http://localhost:8000/")
    print("   Admin panel: http://localhost:8000/admin/")

if __name__ == '__main__':
    crear_datos_ejemplo()
