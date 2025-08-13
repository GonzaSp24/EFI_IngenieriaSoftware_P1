"""
Script mejorado para configurar la base de datos con validaciones
Evita duplicados y valida datos existentes
"""
import os
import sys
import django
from datetime import datetime, timedelta, date
from decimal import Decimal

# Configurar Django
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aerolinea_project.settings')

try:
    django.setup()
    print("✅ Django configurado correctamente")
except Exception as e:
    print(f"❌ Error configurando Django: {e}")
    sys.exit(1)

# Importar modelos
try:
    from vuelos.models import Avion, Vuelo, Asiento
    from pasajeros.models import Pasajero
    from reservas.models import Reserva, Boleto
    from django.contrib.auth.models import User
    from django.db import connection
    print("✅ Modelos importados correctamente")
except ImportError as e:
    print(f"❌ Error importando modelos: {e}")
    sys.exit(1)

def verificar_tablas():
    """Verifica que las tablas existan en la base de datos"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tablas = [row[0] for row in cursor.fetchall()]
            
        tablas_requeridas = [
            'vuelos_avion', 'vuelos_vuelo', 'vuelos_asiento', 
            'pasajeros_pasajero', 
            'reservas_reserva', 'reservas_boleto',
            'auth_user'
        ]
        
        tablas_faltantes = [tabla for tabla in tablas_requeridas if tabla not in tablas]
        
        if tablas_faltantes:
            print(f"❌ Tablas faltantes: {tablas_faltantes}")
            print("Por favor, ejecuta: python manage.py makemigrations && python manage.py migrate")
            return False
        
        print("✅ Todas las tablas necesarias existen")
        return True
        
    except Exception as e:
        print(f"❌ Error verificando tablas: {e}")
        return False

def crear_usuarios():
    """Crear usuarios del sistema con validaciones"""
    print("👤 Verificando/Creando usuarios...")
    
    usuarios_creados = 0
    
    # Superusuario
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@aerolinea.com',
            password='admin123'
        )
        print("✅ Superusuario creado: admin/admin123")
        usuarios_creados += 1
    else:
        print("⚡ Superusuario 'admin' ya existe")
    
    # Usuarios de ejemplo
    usuarios_ejemplo = [
        {
            'username': 'empleado1', 
            'email': 'empleado@aerolinea.com', 
            'password': 'emp123'
        },
        {
            'username': 'cliente1', 
            'email': 'cliente@email.com', 
            'password': 'cli123'
        },
    ]
    
    for user_data in usuarios_ejemplo:
        if not User.objects.filter(username=user_data['username']).exists():
            User.objects.create_user(**user_data)
            print(f"✅ Usuario {user_data['username']} creado")
            usuarios_creados += 1
        else:
            print(f"⚡ Usuario '{user_data['username']}' ya existe")
    
    return usuarios_creados

def crear_asientos_para_avion(avion):
    """Crear asientos automáticamente para un avión si no existen"""
    asientos_existentes = avion.asiento_set.count()
    
    if asientos_existentes > 0:
        print(f"⚡ {avion.modelo} ya tiene {asientos_existentes} asientos")
        return 0
    
    print(f"🪑 Creando asientos para {avion.modelo}...")
    asientos_creados = 0
    
    for fila in range(1, avion.filas + 1):
        for col_idx in range(avion.columnas):
            columna_letra = chr(65 + col_idx)  # A, B, C, D, E, F
            numero_asiento = f"{fila}{columna_letra}"
            
            # Determinar tipo de asiento según la fila
            if fila <= 3:
                tipo = 'primera'
            elif fila <= 10:
                tipo = 'ejecutivo'
            else:
                tipo = 'economico'
            
            # Crear asiento si no existe
            asiento, created = Asiento.objects.get_or_create(
                avion=avion,
                fila=fila,
                columna=columna_letra,
                defaults={
                    'numero': numero_asiento,
                    'tipo': tipo,
                    'estado': 'disponible'
                }
            )
            
            if created:
                asientos_creados += 1
    
    print(f"✅ {asientos_creados} asientos creados para {avion.modelo}")
    return asientos_creados

def crear_aviones():
    """Crear aviones con validaciones"""
    print("✈️  Verificando/Creando aviones...")
    
    aviones_data = [
        {'modelo': 'Boeing 737-800', 'capacidad': 189, 'filas': 32, 'columnas': 6},
        {'modelo': 'Airbus A320', 'capacidad': 180, 'filas': 30, 'columnas': 6},
        {'modelo': 'Embraer E190', 'capacidad': 114, 'filas': 19, 'columnas': 6},
    ]
    
    aviones = []
    aviones_creados = 0
    asientos_creados_total = 0
    
    for data in aviones_data:
        avion, created = Avion.objects.get_or_create(
            modelo=data['modelo'],
            defaults=data
        )
        aviones.append(avion)
        
        if created:
            print(f"✅ Avión {avion.modelo} creado")
            aviones_creados += 1
        else:
            print(f"⚡ Avión '{avion.modelo}' ya existe")
        
        # Crear asientos
        asientos_creados = crear_asientos_para_avion(avion)
        asientos_creados_total += asientos_creados
    
    return aviones, aviones_creados, asientos_creados_total

def crear_vuelos(aviones):
    """Crear vuelos con validaciones"""
    print("🛫 Verificando/Creando vuelos...")
    
    base_date = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
    vuelos_data = [
        {
            'avion': aviones[0],
            'origen': 'Buenos Aires',
            'destino': 'Córdoba',
            'fecha_salida': base_date + timedelta(days=30),
            'duracion': timedelta(hours=1, minutes=30),
            'precio_base': Decimal('25000.00'),
            'estado': 'programado'
        },
        {
            'avion': aviones[1],
            'origen': 'Buenos Aires',
            'destino': 'Mendoza',
            'fecha_salida': base_date + timedelta(days=31),
            'duracion': timedelta(hours=2, minutes=0),
            'precio_base': Decimal('30000.00'),
            'estado': 'programado'
        },
        {
            'avion': aviones[2],
            'origen': 'Córdoba',
            'destino': 'Bariloche',
            'fecha_salida': base_date + timedelta(days=32),
            'duracion': timedelta(hours=2, minutes=45),
            'precio_base': Decimal('35000.00'),
            'estado': 'programado'
        },
        {
            'avion': aviones[0],
            'origen': 'Mendoza',
            'destino': 'Buenos Aires',
            'fecha_salida': base_date + timedelta(days=33),
            'duracion': timedelta(hours=2, minutes=0),
            'precio_base': Decimal('28000.00'),
            'estado': 'programado'
        },
    ]
    
    vuelos = []
    vuelos_creados = 0
    
    for data in vuelos_data:
        data['fecha_llegada'] = data['fecha_salida'] + data['duracion']
        
        # Verificar si ya existe un vuelo similar
        vuelo_existente = Vuelo.objects.filter(
            avion=data['avion'],
            origen=data['origen'],
            destino=data['destino'],
            fecha_salida__date=data['fecha_salida'].date()
        ).first()
        
        if vuelo_existente:
            print(f"⚡ Vuelo {data['origen']} -> {data['destino']} el {data['fecha_salida'].date()} ya existe")
            vuelos.append(vuelo_existente)
        else:
            vuelo = Vuelo.objects.create(**data)
            vuelos.append(vuelo)
            print(f"✅ Vuelo creado: {vuelo.origen} -> {vuelo.destino} el {vuelo.fecha_salida.date()}")
            vuelos_creados += 1
    
    return vuelos, vuelos_creados

def crear_pasajeros():
    """Crear pasajeros con validaciones"""
    print("👥 Verificando/Creando pasajeros...")
    
    pasajeros_data = [
        {
            'nombre': 'Juan Carlos',
            'apellido': 'Pérez',
            'tipo_documento': 'DNI',
            'documento': '12345678',
            'email': 'juan.perez@email.com',
            'telefono': '+54 11 1234-5678',
            'fecha_nacimiento': date(1985, 5, 15)
        },
        {
            'nombre': 'María Elena',
            'apellido': 'González',
            'tipo_documento': 'DNI',
            'documento': '87654321',
            'email': 'maria.gonzalez@email.com',
            'telefono': '+54 11 8765-4321',
            'fecha_nacimiento': date(1990, 8, 22)
        },
        {
            'nombre': 'Carlos Alberto',
            'apellido': 'Rodríguez',
            'tipo_documento': 'PAS',
            'documento': 'AB123456',
            'email': 'carlos.rodriguez@email.com',
            'telefono': '+54 11 5555-1234',
            'fecha_nacimiento': date(1978, 12, 3)
        },
        {
            'nombre': 'Ana Sofía',
            'apellido': 'Martínez',
            'tipo_documento': 'DNI',
            'documento': '11223344',
            'email': 'ana.martinez@email.com',
            'telefono': '+54 11 9876-5432',
            'fecha_nacimiento': date(1992, 3, 10)
        },
    ]
    
    pasajeros = []
    pasajeros_creados = 0
    
    for data in pasajeros_data:
        pasajero, created = Pasajero.objects.get_or_create(
            documento=data['documento'],
            defaults=data
        )
        pasajeros.append(pasajero)
        
        if created:
            print(f"✅ Pasajero creado: {pasajero.nombre} {pasajero.apellido}")
            pasajeros_creados += 1
        else:
            print(f"⚡ Pasajero con documento '{data['documento']}' ya existe")
    
    return pasajeros, pasajeros_creados

def crear_reservas(vuelos, pasajeros):
    """Crear reservas de ejemplo con validaciones"""
    print("🎫 Verificando/Creando reservas...")
    
    if not vuelos or not pasajeros:
        print("⚠️  No hay vuelos o pasajeros para crear reservas")
        return 0
    
    reservas_creadas = 0
    
    # Reserva 1: Juan en vuelo Buenos Aires - Córdoba
    vuelo1 = next((v for v in vuelos if v.origen == 'Buenos Aires' and v.destino == 'Córdoba'), None)
    pasajero1 = next((p for p in pasajeros if p.documento == '12345678'), None)
    
    if vuelo1 and pasajero1:
        # Verificar si ya existe la reserva
        reserva_existente = Reserva.objects.filter(vuelo=vuelo1, pasajero=pasajero1).first()
        
        if not reserva_existente:
            asiento1 = vuelo1.avion.asiento_set.filter(estado='disponible').first()
            
            if asiento1:
                reserva1 = Reserva.objects.create(
                    vuelo=vuelo1,
                    pasajero=pasajero1,
                    asiento=asiento1,
                    precio=vuelo1.precio_base,
                    estado='confirmada'
                )
                
                # Crear boleto
                Boleto.objects.create(reserva=reserva1)
                print(f"✅ Reserva creada: {reserva1.codigo_reserva} para {pasajero1.nombre}")
                reservas_creadas += 1
            else:
                print("⚠️  No hay asientos disponibles para crear reserva")
        else:
            print(f"⚡ Ya existe reserva para {pasajero1.nombre} en vuelo {vuelo1.origen}-{vuelo1.destino}")
    
    # Reserva 2: María en vuelo Buenos Aires - Mendoza
    vuelo2 = next((v for v in vuelos if v.origen == 'Buenos Aires' and v.destino == 'Mendoza'), None)
    pasajero2 = next((p for p in pasajeros if p.documento == '87654321'), None)
    
    if vuelo2 and pasajero2:
        reserva_existente = Reserva.objects.filter(vuelo=vuelo2, pasajero=pasajero2).first()
        
        if not reserva_existente:
            asiento2 = vuelo2.avion.asiento_set.filter(estado='disponible').first()
            
            if asiento2:
                reserva2 = Reserva.objects.create(
                    vuelo=vuelo2,
                    pasajero=pasajero2,
                    asiento=asiento2,
                    precio=vuelo2.precio_base,
                    estado='confirmada'
                )
                
                Boleto.objects.create(reserva=reserva2)
                print(f"✅ Reserva creada: {reserva2.codigo_reserva} para {pasajero2.nombre}")
                reservas_creadas += 1
        else:
            print(f"⚡ Ya existe reserva para {pasajero2.nombre} en vuelo {vuelo2.origen}-{vuelo2.destino}")
    
    return reservas_creadas

def mostrar_resumen():
    """Mostrar resumen de datos en la base de datos"""
    print(f"\n📊 RESUMEN ACTUAL DE LA BASE DE DATOS:")
    print(f"   • Usuarios: {User.objects.count()}")
    print(f"   • Aviones: {Avion.objects.count()}")
    print(f"   • Asientos: {Asiento.objects.count()}")
    print(f"   • Vuelos: {Vuelo.objects.count()}")
    print(f"   • Pasajeros: {Pasajero.objects.count()}")
    print(f"   • Reservas: {Reserva.objects.count()}")
    print(f"   • Boletos: {Boleto.objects.count()}")

def mostrar_fechas_vuelos():
    """Mostrar fechas de vuelos para debugging"""
    vuelos = Vuelo.objects.filter(estado='programado').order_by('fecha_salida')
    if vuelos.exists():
        print(f"\n📅 VUELOS PROGRAMADOS:")
        for vuelo in vuelos:
            print(f"   • {vuelo.origen} -> {vuelo.destino}: {vuelo.fecha_salida.date()} a las {vuelo.fecha_salida.time()}")
    else:
        print(f"\n⚠️  No hay vuelos programados")

def crear_datos_ejemplo():
    """Función principal para crear datos de ejemplo con validaciones"""
    if not verificar_tablas():
        return
    
    print("🚀 INICIANDO CONFIGURACIÓN DE BASE DE DATOS CON VALIDACIONES")
    print("=" * 60)
    
    try:
        # Mostrar estado inicial
        print("📊 Estado inicial:")
        mostrar_resumen()
        print()
        
        # Crear usuarios
        usuarios_creados = crear_usuarios()
        
        # Crear aviones y asientos
        aviones, aviones_creados, asientos_creados = crear_aviones()
        
        # Crear vuelos
        vuelos, vuelos_creados = crear_vuelos(aviones)
        
        # Crear pasajeros
        pasajeros, pasajeros_creados = crear_pasajeros()
        
        # Crear reservas
        reservas_creadas = crear_reservas(vuelos, pasajeros)
        
        # Resumen final
        print("\n" + "=" * 60)
        print("🎉 CONFIGURACIÓN COMPLETADA")
        print("=" * 60)
        
        print(f"\n📈 ELEMENTOS CREADOS EN ESTA EJECUCIÓN:")
        print(f"   • Usuarios nuevos: {usuarios_creados}")
        print(f"   • Aviones nuevos: {aviones_creados}")
        print(f"   • Asientos nuevos: {asientos_creados}")
        print(f"   • Vuelos nuevos: {vuelos_creados}")
        print(f"   • Pasajeros nuevos: {pasajeros_creados}")
        print(f"   • Reservas nuevas: {reservas_creadas}")
        
        mostrar_resumen()
        mostrar_fechas_vuelos()
        
        print(f"\n🔑 CREDENCIALES DE ACCESO:")
        print(f"   • Admin: admin / admin123")
        print(f"   • Empleado: empleado1 / emp123")
        print(f"   • Cliente: cliente1 / cli123")
        
        print(f"\n🌐 URLS DE ACCESO:")
        print(f"   • Aplicación: http://localhost:8000/")
        print(f"   • Panel Admin: http://localhost:8000/admin/")
        
        if vuelos_creados > 0 or Vuelo.objects.filter(estado='programado').exists():
            print(f"\n💡 PARA PROBAR EL BUSCADOR:")
            print(f"   Usa las fechas mostradas arriba en el formato YYYY-MM-DD")
        
    except Exception as e:
        print(f"❌ Error durante la configuración: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    crear_datos_ejemplo()
