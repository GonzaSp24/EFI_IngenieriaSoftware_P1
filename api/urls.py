"""
URLs para la API REST

Este módulo define todas las rutas (endpoints) de la API REST.
Utiliza Django REST Framework Router para los ViewSets y rutas
manuales para las vistas basadas en clases (APIView).

Estructura de URLs:
- /api/schema/ - Esquema OpenAPI de la API
- /api/docs/ - Documentación interactiva Swagger
- /api/redoc/ - Documentación alternativa ReDoc
- /api/auth/* - Endpoints de autenticación
- /api/flight-vs/ - Gestión de vuelos (ViewSet CRUD)
- /api/plane-vs/ - Gestión de aviones (ViewSet CRUD)
- /api/pasajero-vs/ - Gestión de pasajeros (ViewSet CRUD)
- /api/reserva-vs/ - Gestión de reservas (ViewSet CRUD)
- /api/boleto-vs/ - Gestión de boletos (ViewSet solo lectura)
- /api/flightAvailable/ - Listar vuelos disponibles
- /api/flightDetail/<id>/ - Detalle de un vuelo
- /api/flightFilter/ - Filtrar vuelos por origen/destino/fecha
- /api/planeLayout/<id>/ - Layout de asientos de un avión
- /api/checkSeatAvailability/<plane_id>/<seat_code>/ - Verificar disponibilidad de asiento
- /api/availableSeats/<flight_id>/ - Asientos disponibles de un vuelo
- /api/passengerDetail/<id>/ - Detalle de un pasajero
- /api/reservationsByPassenger/<id>/ - Reservas de un pasajero
- /api/createReservation/ - Crear una reserva
- /api/changeReservationStatus/<id>/ - Cambiar el estado de una reserva
- /api/generateTicket/<id>/ - Generar un boleto
- /api/ticketInformation/<barcode>/ - Información de un boleto
- /api/passengersByFlight/<id>/ - Pasajeros de un vuelo
- /api/activeReservations/<id>/ - Reservas activas de un pasajero
- /api/reportes/pasajeros-vuelo/<vuelo_id>/ - Reporte de pasajeros por vuelo
- /api/reportes/reservas-activas/<pasajero_id>/ - Reporte de reservas activas de pasajero
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from api.views import (
    FlightViewSet,
    PlaneViewSet,
    PasajeroViewSet,
    ReservaViewSet,
    BoletoViewSet,
    FlightAvailableListAPIView,
    FlightDetailAPIView,
    FlightFilterAPIView,
    PlaneLayoutAPIView,
    SeatAvailabilityAPIView,
    AvailableSeatsListAPIView,
    PassengerDetailAPIView,
    ReservationByPassengerAPIView,
    CreateReservationAPIView,
    ChangeReservationStatusAPIView,
    GenerateTicketAPIView,
    TicketInformationAPIView,
    RegisterView,
    LoginView,
    PasajerosPorVueloView,
    ReservasActivasPasajeroView,
)


# ============================================================================
# ROUTER PARA VIEWSETS
# ============================================================================
# Los ViewSets proporcionan automáticamente las operaciones CRUD:
# - GET /resource/ - Listar todos
# - POST /resource/ - Crear nuevo
# - GET /resource/{id}/ - Obtener uno
# - PUT /resource/{id}/ - Actualizar completo
# - PATCH /resource/{id}/ - Actualizar parcial
# - DELETE /resource/{id}/ - Eliminar
router = DefaultRouter()
router.register(r"flight-vs", FlightViewSet, basename="flight")
router.register(r"plane-vs", PlaneViewSet, basename="plane")
router.register(r"pasajero-vs", PasajeroViewSet, basename="pasajero")
router.register(r"reserva-vs", ReservaViewSet, basename="reserva")
router.register(r"boleto-vs", BoletoViewSet, basename="boleto")

urlpatterns = [
    # ==== Documentación OpenAPI ====
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # ==== Autenticación ====
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # ==== Endpoints personalizados ====
    path(
        "flightAvailable/",
        FlightAvailableListAPIView.as_view(),
        name="flight-available",
    ),
    path("flightDetail/<int:pk>/", FlightDetailAPIView.as_view(), name="flight-detail"),
    path("flightFilter/", FlightFilterAPIView.as_view(), name="flight-filter"),
    path(
        "planeLayout/<int:plane_id>/", PlaneLayoutAPIView.as_view(), name="plane-layout"
    ),
    path(
        "checkSeatAvailability/<int:plane_id>/<str:seat_code>/",
        SeatAvailabilityAPIView.as_view(),
        name="seat-availability",
    ),
    path(
        "availableSeats/<int:flight_id>/",
        AvailableSeatsListAPIView.as_view(),
        name="available-seats",
    ),
    path(
        "passengerDetail/<int:pk>/",
        PassengerDetailAPIView.as_view(),
        name="passenger-detail",
    ),
    path(
        "reservationsByPassenger/<int:passenger_id>/",
        ReservationByPassengerAPIView.as_view(),
        name="reservations-by-passenger",
    ),
    path(
        "createReservation/",
        CreateReservationAPIView.as_view({"post": "create"}),
        name="create-reservation",
    ),
    path(
        "changeReservationStatus/<int:reservation_id>/",
        ChangeReservationStatusAPIView.as_view(),
        name="change-reservation-status",
    ),
    path(
        "generateTicket/<int:reservation_id>/",
        GenerateTicketAPIView.as_view(),
        name="generate-ticket",
    ),
    path(
        "ticketInformation/<str:barcode>/",
        TicketInformationAPIView.as_view(),
        name="ticket-information",
    ),
    path(
        "reportes/pasajeros-vuelo/<int:vuelo_id>/",
        PasajerosPorVueloView.as_view(),
        name="reporte-pasajeros-vuelo",
    ),
    path(
        "reportes/reservas-activas/<int:pasajero_id>/",
        ReservasActivasPasajeroView.as_view(),
        name="reporte-reservas-activas",
    ),
    # ==== CRUDs de ViewSets ====
    path("", include(router.urls)),
]
