"""
Vistas de la API REST
Todas las vistas en un solo archivo siguiendo el patrón de Mile
"""

from rest_framework import viewsets, status
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.utils.crypto import get_random_string
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
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
    LoginSerializer,
    RegisterSerializer,
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
        return VueloService.get_upcoming_flights()


class FlightDetailAPIView(AuthView, RetrieveAPIView):
    """
    GET /api/flightDetail/<pk>/
    Detalle completo de un vuelo (asientos, reservas, etc.).
    """
    permission_classes = [IsAuthenticated]
    serializer_class = VueloDetailSerializer
    lookup_field = "pk"  # explícito: tomamos <pk> de la URL

    @extend_schema(responses=VueloDetailSerializer)
    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        ser = self.get_serializer(obj)
        return Response(ser.data)

    def get_object(self):
        """
        Obtiene un Vuelo POR MODELO usando el service.
        Importantísimo: el service debe devolver instancia de Vuelo,
        no dict. Idealmente con select_related/prefetch para performance.
        """
        vuelo_id = self.kwargs.get("pk")
        vuelo = VueloService.get_vuelo(vuelo_id)
        if vuelo is None:
            raise NotFound("Vuelo no encontrado")

        # Si el service no aplica prefetch, reforzá acá:
        # (Evita N+1 al serializar asientos y reservas)
        return (
            Vuelo.objects
            .select_related("avion")
            .prefetch_related(
                "avion__asiento_set",
                "reservas__pasajero",
                "reservas__asiento",
            )
            .get(pk=vuelo.pk)
        )


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
    pagination_class = None

    def get(self, request, pk):
        avion = AvionService.get_avion(pk)
        if not avion:
            raise NotFound("Avión no encontrado")

        asientos = avion.asiento_set.all().order_by("fila", "columna")
        avion_data = AvionSerializer(avion).data
        asientos_data = AsientoSerializer(asientos, many=True).data

        return Response({
            "avion": avion_data,
            "asientos": asientos_data
        })


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
        data = AsientoService.check_disponibilidad(plane_id, seat_code)
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
        return AsientoService.get_asientos_by_avion(flight_id)


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
        return PasajeroService.get_pasajero(pasajero_id)


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
        return ReservaService.get_reserva(passenger_id)


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
        reserva = ReservaService.create_reserva(
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
            reserva = ReservaService.get_reserva(reservation_id)
        except ValueError:
            return Response(
                {"error": "La reserva no existe."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = ReservaSerializer(reserva)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, reservation_id=None):
        """Cambia el estado de una reserva"""
        try:
            reserva = ReservaService.get_reserva(reservation_id)
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
        boleto = BoletoService.create_boleto(reservation_id)

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
        data = BoletoService.get_boleto_by_codigo(barcode)
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
    Crea un usuario Django y su pasajero asociado. Devuelve tokens JWT.
    """
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    @extend_schema(
        request=RegisterSerializer,
        responses={
            201: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
        },
    )
    def post(self, request):
        # Validación con serializer
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        v = ser.validated_data

        # Reglas simples de unicidad
        if User.objects.filter(email=v.get("email") or "").exists():
            return Response({"error": "El email ya está registrado."}, status=400)
        if User.objects.filter(username=v["username"]).exists():
            return Response({"error": "El username ya está registrado."}, status=400)

        # Crear usuario
        user = User.objects.create_user(
            username=v["username"],
            email=v.get("email", ""),
            password=v["password"],
            first_name=v.get("first_name", ""),
            last_name=v.get("last_name", ""),
        )

        # Crear pasajero usando tus datos del body
        pasajero = PasajeroService.create_pasajero(
            nombre=request.data.get("nombre", user.first_name or user.username),
            apellido=request.data.get("apellido", user.last_name or ""),
            documento=request.data.get("documento", ""),
            tipo_documento=request.data.get("tipo_documento", "DNI"),
            email=user.email or f"{user.username}@example.com",
            telefono=request.data.get("telefono", ""),
            fecha_nacimiento=request.data.get("fecha_nacimiento", None),
            usuario=user,  # si querés linkear OneToOne en el alta
        )

        # JWT
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
    Acepta username o email + password. Devuelve tokens JWT.
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
        },
    )
    def post(self, request):
        ser = LoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        username_or_email = ser.validated_data["username"]
        password = ser.validated_data["password"]

        # 1) intentar con username directo
        user = authenticate(username=username_or_email, password=password)

        # 2) si falla, buscar por email y reintentar con el username real
        if not user:
            try:
                u = User.objects.get(email=username_or_email)
                user = authenticate(username=u.username, password=password)
            except User.DoesNotExist:
                user = None

        if not user:
            return Response({"error": "Credenciales inválidas."}, status=401)

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
            status=200,
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
            vuelo = VueloService.get_vuelo(vuelo_id)
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
                return Response(
                    {"error": "No tiene permisos para ver este reporte."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            pasajero = PasajeroService.get_pasajero(pasajero_id)
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
