"""
Vistas de la API REST
Todas las vistas en un solo archivo siguiendo el patrón de Mile
"""

from rest_framework import viewsets, status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.utils.crypto import get_random_string
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from airline.models import Vuelo, Avion, Asiento, Pasajero, Reserva, Boleto

from api.serializers import (
    VueloSerializer,
    VueloListSerializer,
    VueloDetailSerializer,
    AvionSerializer,
    AsientoSerializer,
    PasajeroSerializer,
    ReservaSerializer,
    BoletoSerializer,
)

from api.mixins import AuthView, AuthAdminView
from airline.services import (
    VueloService,
    AvionService,
    AsientoService,
    PasajeroService,
    ReservaService,
    BoletoService,
)

# ============================================================================
# GESTIÓN DE VUELOS (API)
# ============================================================================


class FlightAvailableListAPIView(AuthView, ListAPIView):
    """
    GET /api/flightAvailable/
    Filtra los vuelos disponibles que sean mayor a la fecha de hoy.
    Accesible para cualquier usuario autenticado.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = VueloListSerializer

    def get_queryset(self):
        """Obtiene vuelos disponibles usando el servicio"""
        return VueloService.obtener_vuelos_proximos()


class FlightDetailAPIView(AuthView, RetrieveAPIView):
    """
    GET /api/flightDetail/<pk>/
    Da el detalle completo de un vuelo específico.
    Accesible para cualquier usuario autenticado.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = VueloDetailSerializer

    def get_object(self):
        """Obtiene un vuelo por ID usando el servicio"""
        vuelo_id = self.kwargs.get("pk")
        try:
            return VueloService.obtener_por_id(vuelo_id)
        except Vuelo.DoesNotExist:
            from rest_framework.exceptions import NotFound

            raise NotFound(detail="Vuelo no encontrado")


@extend_schema(
    parameters=[
        OpenApiParameter("origen", OpenApiTypes.STR, description="Ciudad de origen"),
        OpenApiParameter("destino", OpenApiTypes.STR, description="Ciudad de destino"),
        OpenApiParameter(
            "fecha", OpenApiTypes.DATE, description="Fecha de salida (YYYY-MM-DD)"
        ),
    ]
)
class FlightFilterAPIView(AuthView, ListAPIView):
    """
    GET /api/flightFilter/?origen=<ciudad>&destino=<ciudad>&fecha=<YYYY-MM-DD>
    Filtra vuelos por origen, destino y fecha de salida.
    Si no se envía filtro, devuelve todos los vuelos.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = VueloListSerializer
    pagination_class = None

    def get_queryset(self):
        """Filtra vuelos según parámetros de consulta"""
        origen = self.request.query_params.get("origen")
        destino = self.request.query_params.get("destino")
        fecha = self.request.query_params.get("fecha")

        return VueloService.filtrar_vuelos(origen, destino, fecha)


class FlightViewSet(AuthAdminView, viewsets.ModelViewSet):
    """
    CRUD completo de vuelos (solo para admins)
    - GET /api/flight-vs/
    - POST /api/flight-vs/
    - GET /api/flight-vs/{id}/
    - PUT /api/flight-vs/{id}/
    - PATCH /api/flight-vs/{id}/
    - DELETE /api/flight-vs/{id}/
    """

    queryset = Vuelo.objects.all().order_by("id")
    serializer_class = VueloSerializer


# ============================================================================
# GESTIÓN DE AVIONES Y ASIENTOS (API)
# ============================================================================


class PlaneViewSet(AuthAdminView, viewsets.ModelViewSet):
    """
    CRUD completo de aviones (solo para admins)
    - GET /api/plane-vs/
    - POST /api/plane-vs/
    - GET /api/plane-vs/{id}/
    - PUT /api/plane-vs/{id}/
    - PATCH /api/plane-vs/{id}/
    - DELETE /api/plane-vs/{id}/
    """

    queryset = Avion.objects.all().order_by("id")
    serializer_class = AvionSerializer
    permission_classes = [IsAuthenticated]


class PlaneLayoutAPIView(AuthAdminView, ListAPIView):
    """
    GET /api/planeLayout/<int:plane_id>/
    Devuelve el layout de los asientos del avión.
    Muestra la distribución completa de asientos con su estado.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = AsientoSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def list(self, request, plane_id):
        """Obtiene el layout del avión usando el servicio"""
        data = AvionService.obtener_layout_avion(plane_id)
        if not data:
            return Response(
                {"error": "El avión no existe."}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(data, status=status.HTTP_200_OK)


class SeatAvailabilityAPIView(AuthView, RetrieveAPIView):
    """
    GET /api/checkSeatAvailability/<int:plane_id>/<str:seat_code>/
    Verifica si un asiento existe y muestra su estado actual.
    Ejemplo: /api/checkSeatAvailability/4/1A/
    """

    permission_classes = [IsAuthenticated]
    serializer_class = AsientoSerializer

    def get(self, request, plane_id, seat_code):
        """Verifica disponibilidad de un asiento específico"""
        data = AsientoService.verificar_disponibilidad(plane_id, seat_code)
        if not data:
            return Response(
                {"error": "El asiento no existe."}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(data, status=status.HTTP_200_OK)


class AvailableSeatsListAPIView(AuthView, ListAPIView):
    """
    GET /api/availableSeats/<int:flight_id>/
    Devuelve los asientos disponibles de un vuelo indicado
    según el avión asociado al vuelo.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = AsientoSerializer

    def get_queryset(self):
        """Obtiene asientos disponibles para un vuelo"""
        flight_id = self.kwargs.get("flight_id")
        return AsientoService.obtener_asientos_disponibles_por_vuelo(flight_id)


# ============================================================================
# GESTIÓN DE PASAJEROS (API)
# ============================================================================


class PasajeroViewSet(AuthAdminView, viewsets.ModelViewSet):
    """
    CRUD completo de pasajeros (solo para admins)
    - GET /api/pasajero-vs/
    - POST /api/pasajero-vs/
    - GET /api/pasajero-vs/{id}/
    - PUT /api/pasajero-vs/{id}/
    - PATCH /api/pasajero-vs/{id}/
    - DELETE /api/pasajero-vs/{id}/
    """

    queryset = Pasajero.objects.all().order_by("id")
    serializer_class = PasajeroSerializer


class PassengerDetailAPIView(AuthView, RetrieveAPIView):
    """
    GET /api/passengerDetail/<pk>/
    Da el detalle de un pasajero.
    Accesible para cualquier usuario autenticado.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = PasajeroSerializer

    def get_object(self):
        """Obtiene un pasajero por ID"""
        pasajero_id = self.kwargs.get("pk")
        return PasajeroService.obtener_por_id(pasajero_id)


class ReservationByPassengerAPIView(AuthView, ListAPIView):
    """
    GET /api/reservationsByPassenger/<int:passenger_id>/
    Devuelve todas las reservas asociadas a un pasajero.
    Accesible para cualquier usuario autenticado.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ReservaSerializer
    pagination_class = None

    def get_queryset(self):
        """Obtiene reservas de un pasajero"""
        passenger_id = self.kwargs.get("passenger_id")
        return ReservaService.obtener_por_pasajero(passenger_id)


# ============================================================================
# SISTEMA DE RESERVAS (API)
# ============================================================================


class CreateReservationAPIView(AuthAdminView, viewsets.ViewSet):
    """
    POST /api/createReservation/
    Crea una reserva para un pasajero en un vuelo (solo para admin).
    El asiento debe estar disponible.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ReservaSerializer

    def create(self, request):
        """Crea una nueva reserva"""
        data = request.data.copy()

        vuelo_id = data.get("vuelo")
        pasajero_id = data.get("pasajero")
        asiento_id = data.get("asiento")
        usuario_id = data.get("usuario")

        # Validaciones básicas
        if not (vuelo_id and pasajero_id and asiento_id and usuario_id):
            return Response(
                {"error": "Faltan campos obligatorios."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            vuelo = Vuelo.objects.get(pk=vuelo_id)
            pasajero = Pasajero.objects.get(pk=pasajero_id)
            asiento = Asiento.objects.get(pk=asiento_id)
        except (Vuelo.DoesNotExist, Pasajero.DoesNotExist, Asiento.DoesNotExist):
            return Response(
                {"error": "Alguno de los objetos referenciados no existe."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Verifica si el asiento está disponible
        if asiento.estado.lower() != "disponible":
            return Response(
                {"error": "El asiento no está disponible."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Genera código único de reserva
        codigo_reserva = get_random_string(10).upper()

        # Usa el precio_base del vuelo
        precio = vuelo.precio_base

        # Crear la reserva usando el servicio
        reserva = ReservaService.crear_reserva(
            vuelo_id=vuelo_id,
            pasajero_id=pasajero_id,
            asiento_id=asiento_id,
            usuario_id=usuario_id,
            precio=precio,
            codigo_reserva=codigo_reserva,
        )

        # Marca asiento como ocupado
        asiento.estado = "ocupado"
        asiento.save()

        serializer = ReservaSerializer(reserva)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ChangeReservationStatusAPIView(AuthAdminView, APIView):
    """
    PATCH /api/changeReservationStatus/<int:reservation_id>/
    Permite que un administrador cambie el estado de una reserva.
    """

    permission_classes = [IsAdminUser]
    serializer_class = ReservaSerializer

    def get(self, request, reservation_id=None):
        """GET opcional solo para Swagger / testing"""
        try:
            reserva = ReservaService.obtener_por_id(reservation_id)
        except ValueError:
            return Response(
                {"error": "La reserva no existe."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = ReservaSerializer(reserva)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, reservation_id=None):
        """Cambia el estado de una reserva"""
        try:
            reserva = ReservaService.obtener_por_id(reservation_id)
        except ValueError:
            return Response(
                {"error": "La reserva no existe."}, status=status.HTTP_404_NOT_FOUND
            )

        nuevo_estado = request.data.get("estado")
        if not nuevo_estado:
            return Response(
                {"error": "Debe proporcionar un nuevo estado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Cambia el estado usando el service
        reserva_actualizada = ReservaService.cambiar_estado(
            reservation_id, nuevo_estado.lower()
        )

        serializer = ReservaSerializer(reserva_actualizada)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReservaViewSet(AuthAdminView, viewsets.ModelViewSet):
    """
    CRUD completo de reservas (solo para admins)
    - GET /api/reserva-vs/
    - POST /api/reserva-vs/
    - GET /api/reserva-vs/{id}/
    - PUT /api/reserva-vs/{id}/
    - PATCH /api/reserva-vs/{id}/
    - DELETE /api/reserva-vs/{id}/
    """

    queryset = Reserva.objects.all().order_by("id")
    serializer_class = ReservaSerializer


# ============================================================================
# BOLETOS (API)
# ============================================================================


class GenerateTicketAPIView(AuthAdminView, APIView):
    """
    POST /api/generateTicket/<int:reservation_id>/
    Crea un boleto (ticket) a partir de una reserva confirmada.
    El código de barras se genera automáticamente.
    Solo para admin.
    """

    permission_classes = [IsAdminUser]
    serializer_class = BoletoSerializer

    def post(self, request, reservation_id):
        """Genera un boleto para una reserva confirmada"""
        try:
            reserva = Reserva.objects.get(pk=reservation_id)
        except Reserva.DoesNotExist:
            return Response(
                {"error": "La reserva no existe."}, status=status.HTTP_404_NOT_FOUND
            )

        # Ver si la reserva está confirmada
        if reserva.estado.lower() != "confirmada":
            return Response(
                {
                    "error": "Solo se puede generar un boleto a partir de una reserva confirmada."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Ver si ya existe un boleto para esta reserva
        if Boleto.objects.filter(reserva=reserva).exists():
            return Response(
                {"error": "Ya existe un boleto para esta reserva."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Crear el boleto usando el servicio
        boleto = BoletoService.crear_boleto(reservation_id)

        serializer = BoletoSerializer(boleto)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TicketInformationAPIView(AuthView, RetrieveAPIView):
    """
    GET /api/ticketInformation/<str:barcode>/
    Buscar un ticket por su código de barras.
    Ejemplo: /api/ticketInformation/Y8C5TLQEGZ39
    """

    permission_classes = [IsAuthenticated]
    serializer_class = BoletoSerializer

    def get(self, request, barcode):
        """Obtiene información de un boleto por código de barras"""
        data = BoletoService.obtener_info_boleto(barcode)
        if not data:
            return Response(
                {"error": "El ticket no existe."}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(data, status=status.HTTP_200_OK)


class BoletoViewSet(AuthAdminView, viewsets.ModelViewSet):
    """
    CRUD completo de boletos (solo para admins)
    - GET /api/boleto-vs/
    - POST /api/boleto-vs/
    - GET /api/boleto-vs/{id}/
    - PUT /api/boleto-vs/{id}/
    - PATCH /api/boleto-vs/{id}/
    - DELETE /api/boleto-vs/{id}/
    """

    queryset = Boleto.objects.all().order_by("id")
    serializer_class = BoletoSerializer


# ============================================================================
# AUTENTICACIÓN (API)
# ============================================================================


class RegisterView(APIView):
    """
    POST /api/auth/register/
    Registrar un nuevo usuario y pasajero.
    Crea automáticamente un usuario de Django y un pasajero asociado.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """Registra un nuevo usuario y pasajero"""
        from rest_framework_simplejwt.tokens import RefreshToken
        from django.contrib.auth.models import User

        data = request.data

        # Validaciones básicas
        required_fields = [
            "nombre",
            "apellido",
            "documento",
            "email",
            "password",
            "tipo_documento",
            "fecha_nacimiento",
        ]
        for field in required_fields:
            if not data.get(field):
                return Response(
                    {"error": f"El campo {field} es obligatorio."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Verificar si el email ya existe
        if User.objects.filter(email=data["email"]).exists():
            return Response(
                {"error": "El email ya está registrado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Crear usuario
        username = data["email"].split("@")[0]
        user = User.objects.create_user(
            username=username, email=data["email"], password=data["password"]
        )

        # Crear pasajero usando el servicio
        pasajero = PasajeroService.crear_pasajero(
            nombre=data["nombre"],
            apellido=data["apellido"],
            documento=data["documento"],
            tipo_documento=data["tipo_documento"],
            email=data["email"],
            telefono=data.get("telefono", ""),
            fecha_nacimiento=data["fecha_nacimiento"],
            nacionalidad=data.get("nacionalidad", ""),
        )

        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "pasajero_id": pasajero.id,
                },
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """
    POST /api/auth/login/
    Iniciar sesión con username/email y password.
    Retorna tokens JWT (access y refresh).
    """

    permission_classes = [AllowAny]
    
    def post(self, request):
        """Inicia sesión y retorna tokens JWT"""
        from rest_framework_simplejwt.tokens import RefreshToken
        from django.contrib.auth import authenticate
        from django.contrib.auth.models import User

        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Debe proporcionar username y password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Intentar autenticar con username
        user = authenticate(username=username, password=password)

        # Si no funciona, intentar con email
        if not user:
            try:
                user_obj = User.objects.get(email=username)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass

        if user:
            # Generar tokens JWT
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "is_staff": user.is_staff,
                    },
                    "tokens": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"error": "Credenciales inválidas."}, status=status.HTTP_401_UNAUTHORIZED
        )


# ============================================================================
# REPORTES (API)
# ============================================================================


class PasajerosPorVueloView(APIView):
    """
    GET /api/reportes/pasajeros-vuelo/<int:vuelo_id>/
    Lista de pasajeros con reservas confirmadas en un vuelo.
    Solo accesible para administradores.
    """

    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, vuelo_id):
        """Obtiene lista de pasajeros de un vuelo"""
        try:
            vuelo = VueloService.obtener_por_id(vuelo_id)
            reservas = Reserva.objects.filter(
                vuelo_id=vuelo_id, estado="confirmada"
            ).select_related("pasajero")

            pasajeros = [reserva.pasajero for reserva in reservas]
            serializer = PasajeroSerializer(pasajeros, many=True)

            return Response(
                {
                    "vuelo": f"{vuelo.origen} → {vuelo.destino}",
                    "fecha": vuelo.fecha_salida,
                    "total_pasajeros": len(pasajeros),
                    "pasajeros": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Vuelo.DoesNotExist:
            return Response(
                {"error": "El vuelo no existe."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ReservasActivasPasajeroView(APIView):
    """
    GET /api/reportes/reservas-activas/<int:pasajero_id>/
    Devuelve todas las reservas activas (confirmadas) de un pasajero.
    Accesible para administradores o el mismo pasajero.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, pasajero_id):
        """Obtiene reservas activas de un pasajero"""
        try:
            # Verificar permisos: admin o el mismo pasajero
            if not request.user.is_staff:
                # Aquí deberías verificar si el usuario es el dueño del pasajero
                # Por ahora permitimos solo a admins
                return Response(
                    {"error": "No tiene permisos para ver este reporte."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            pasajero = PasajeroService.obtener_por_id(pasajero_id)
            reservas = Reserva.objects.filter(
                pasajero_id=pasajero_id, estado="confirmada"
            ).select_related("vuelo", "asiento")

            serializer = ReservaSerializer(reservas, many=True)

            return Response(
                {
                    "pasajero": f"{pasajero.nombre} {pasajero.apellido}",
                    "total_reservas_activas": reservas.count(),
                    "reservas": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Pasajero.DoesNotExist:
            return Response(
                {"error": "El pasajero no existe."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
