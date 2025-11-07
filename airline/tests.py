"""
Tests para la aplicación airline.
Incluye tests para modelos, services, repositories y vistas.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from decimal import Decimal

from airline.models import Avion, Vuelo, Pasajero, Reserva, Boleto, Asiento
from airline.services.vuelo_service import VueloService
from airline.services.pasajero_service import PasajeroService
from airline.services.reserva_service import ReservaService


class AvionModelTest(TestCase):
    """Tests para el modelo Avion"""

    def setUp(self):
        self.avion = Avion.objects.create(
            modelo="Boeing 737", capacidad=180, fabricante="Boeing"
        )

    def test_avion_creation(self):
        """Test de creación de avión"""
        self.assertEqual(self.avion.modelo, "Boeing 737")
        self.assertEqual(self.avion.capacidad, 180)
        self.assertTrue(self.avion.activo)

    def test_avion_str(self):
        """Test del método __str__"""
        self.assertEqual(str(self.avion), "Boeing 737")


class VueloModelTest(TestCase):
    """Tests para el modelo Vuelo"""

    def setUp(self):
        self.avion = Avion.objects.create(
            modelo="Airbus A320", capacidad=150, fabricante="Airbus"
        )
        self.vuelo = Vuelo.objects.create(
            numero_vuelo="AA123",
            origen="Buenos Aires",
            destino="Madrid",
            fecha_salida=datetime.now() + timedelta(days=7),
            fecha_llegada=datetime.now() + timedelta(days=7, hours=12),
            avion=self.avion,
            precio=Decimal("500.00"),
            asientos_disponibles=150,
        )

    def test_vuelo_creation(self):
        """Test de creación de vuelo"""
        self.assertEqual(self.vuelo.numero_vuelo, "AA123")
        self.assertEqual(self.vuelo.origen, "Buenos Aires")
        self.assertEqual(self.vuelo.destino, "Madrid")
        self.assertEqual(self.vuelo.asientos_disponibles, 150)

    def test_vuelo_str(self):
        """Test del método __str__"""
        expected = f"AA123 - Buenos Aires a Madrid"
        self.assertEqual(str(self.vuelo), expected)


class PasajeroModelTest(TestCase):
    """Tests para el modelo Pasajero"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.pasajero = Pasajero.objects.create(
            usuario=self.user,
            nombre="Juan",
            apellido="Pérez",
            dni="12345678",
            email="juan@example.com",
            telefono="1234567890",
        )

    def test_pasajero_creation(self):
        """Test de creación de pasajero"""
        self.assertEqual(self.pasajero.nombre, "Juan")
        self.assertEqual(self.pasajero.apellido, "Pérez")
        self.assertEqual(self.pasajero.dni, "12345678")

    def test_pasajero_str(self):
        """Test del método __str__"""
        self.assertEqual(str(self.pasajero), "Juan Pérez")


class VueloServiceTest(TestCase):
    """Tests para VueloService"""

    def setUp(self):
        self.avion = Avion.objects.create(
            modelo="Boeing 777", capacidad=300, fabricante="Boeing"
        )
        self.service = VueloService()

    def test_listar_vuelos_disponibles(self):
        """Test de listar vuelos disponibles"""
        Vuelo.objects.create(
            numero_vuelo="BA456",
            origen="Londres",
            destino="Nueva York",
            fecha_salida=datetime.now() + timedelta(days=5),
            fecha_llegada=datetime.now() + timedelta(days=5, hours=8),
            avion=self.avion,
            precio=Decimal("800.00"),
            asientos_disponibles=300,
        )

        vuelos = self.service.listar_vuelos_disponibles()
        self.assertEqual(len(vuelos), 1)
        self.assertEqual(vuelos[0].numero_vuelo, "BA456")


class ReservaServiceTest(TestCase):
    """Tests para ReservaService"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser2", password="testpass123"
        )
        self.pasajero = Pasajero.objects.create(
            usuario=self.user,
            nombre="María",
            apellido="García",
            dni="87654321",
            email="maria@example.com",
        )
        self.avion = Avion.objects.create(
            modelo="Airbus A380", capacidad=500, fabricante="Airbus"
        )
        self.vuelo = Vuelo.objects.create(
            numero_vuelo="IB789",
            origen="Madrid",
            destino="Buenos Aires",
            fecha_salida=datetime.now() + timedelta(days=10),
            fecha_llegada=datetime.now() + timedelta(days=10, hours=14),
            avion=self.avion,
            precio=Decimal("600.00"),
            asientos_disponibles=500,
        )
        self.asiento = Asiento.objects.create(
            avion=self.avion, numero_asiento="12A", clase="economica", disponible=True
        )
        self.service = ReservaService()

    def test_crear_reserva(self):
        """Test de creación de reserva"""
        reserva = self.service.crear_reserva(
            vuelo_id=self.vuelo.id,
            pasajero_id=self.pasajero.id,
            asiento_id=self.asiento.id,
        )

        self.assertIsNotNone(reserva)
        self.assertEqual(reserva.vuelo, self.vuelo)
        self.assertEqual(reserva.pasajero, self.pasajero)
        self.assertEqual(reserva.estado, "confirmada")


class VueloViewTest(TestCase):
    """Tests para las vistas de vuelos"""

    def setUp(self):
        self.client = Client()
        self.avion = Avion.objects.create(
            modelo="Boeing 787", capacidad=250, fabricante="Boeing"
        )
        self.vuelo = Vuelo.objects.create(
            numero_vuelo="LA123",
            origen="Santiago",
            destino="Lima",
            fecha_salida=datetime.now() + timedelta(days=3),
            fecha_llegada=datetime.now() + timedelta(days=3, hours=3),
            avion=self.avion,
            precio=Decimal("200.00"),
            asientos_disponibles=250,
        )

    def test_lista_vuelos_view(self):
        """Test de la vista de lista de vuelos"""
        response = self.client.get("/vuelos/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "LA123")

    def test_detalle_vuelo_view(self):
        """Test de la vista de detalle de vuelo"""
        response = self.client.get(f"/vuelos/{self.vuelo.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Santiago")
        self.assertContains(response, "Lima")
