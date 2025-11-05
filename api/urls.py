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

from api.views import (
    # Vuelos y Aviones
    FlightViewSet, PlaneViewSet,
    FlightAvailableListAPIView, FlightDetailAPIView, FlightFilterAPIView,
    PlaneLayoutAPIView, SeatAvailabilityAPIView, AvailableSeatsListAPIView,
    # Pasajeros
    PasajeroViewSet, PassengerDetailAPIView, ReservationByPassengerAPIView,
    # Reservas y Boletos
    ReservaViewSet, BoletoViewSet,
    CreateReservationAPIView, ChangeReservationStatusAPIView,
    GenerateTicketAPIView, TicketInformationAPIView,
    # Autenticación
    RegisterView, LoginView,
    # Reportes
    PasajerosPorVueloView, ReservasActivasPasajeroView,
#     PassengersByFlightAPIView, ActiveReservationsByPassengerAPIView,
)

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# ============================================================================
# CONFIGURACIÓN DE SWAGGER/OPENAPI
# ============================================================================
schema_view = get_schema_view(
    openapi.Info(
        title="API Aerolínea - Sistema de Reservas",
        default_version='v1',
        description="""
        API REST para el sistema de gestión de aerolínea.
        
        Funcionalidades principales:
        - Gestión de vuelos, aviones y asientos
        - Registro y gestión de pasajeros
        - Sistema de reservas con confirmación/cancelación
        - Generación de boletos electrónicos
        - Reportes de pasajeros y reservas
        - Autenticación JWT
        
        Autenticación:
        - Usar el endpoint /api/auth/login/ para obtener tokens
        - Incluir el token en el header: Authorization: Bearer {token}
        """,
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@aerolinea.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
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

router.register(r'flight-vs', FlightViewSet, basename='flight')
router.register(r'plane-vs', PlaneViewSet, basename='plane')
router.register(r'pasajero-vs', PasajeroViewSet, basename='pasajero')
router.register(r'reserva-vs', ReservaViewSet, basename='reserva')
router.register(r'boleto-vs', BoletoViewSet, basename='boleto')

urlpatterns = [
    # ========== DOCUMENTACIÓN ==========
    # Interfaz Swagger para probar la API interactivamente
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # Interfaz ReDoc (alternativa a Swagger, más limpia)
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # Esquema OpenAPI en formato JSON
    path('schema/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    # ========== AUTENTICACIÓN ==========
    # POST /api/auth/register/ - Registro de nuevos usuarios
    # Body: {username, email, password, first_name, last_name}
    path('auth/register/', RegisterView.as_view(), name='register'),
    
    # POST /api/auth/login/ - Login (obtener tokens JWT)
    # Body: {username, password}
    # Response: {access, refresh, user}
    path('auth/login/', LoginView.as_view(), name='login'),
    
    # POST /api/auth/token/refresh/ - Refrescar token de acceso
    # Body: {refresh}
    # Response: {access}
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # ========== VUELOS - ENDPOINTS ADICIONALES ==========
    # GET /api/flightAvailable/ - Listar vuelos disponibles (fecha futura)
    path('flightAvailable/', FlightAvailableListAPIView.as_view(), name='flight-available'),
    
    # GET /api/flightDetail/<pk>/ - Detalle completo de un vuelo
    path('flightDetail/<int:pk>/', FlightDetailAPIView.as_view(), name='flight-detail'),
    
    # GET /api/flightFilter/ - Filtrar vuelos por origen/destino/fecha
    # Query params: ?origin=...&destination=...&date=YYYY-MM-DD
    path('flightFilter/', FlightFilterAPIView.as_view(), name='flight-filter'),
    
    # ========== AVIONES Y ASIENTOS - ENDPOINTS ADICIONALES ==========
    # GET /api/planeLayout/<plane_id>/ - Layout de asientos de un avión
    path('planeLayout/<int:plane_id>/', PlaneLayoutAPIView.as_view(), name='plane-layout'),
    
    # GET /api/checkSeatAvailability/<plane_id>/<seat_code>/ - Verificar disponibilidad de asiento
    path('checkSeatAvailability/<int:plane_id>/<str:seat_code>/', 
         SeatAvailabilityAPIView.as_view(), name='seat-availability'),
    
    # GET /api/availableSeats/<flight_id>/ - Asientos disponibles de un vuelo
    path('availableSeats/<int:flight_id>/', 
         AvailableSeatsListAPIView.as_view(), name='available-seats'),
    
    # ========== PASAJEROS - ENDPOINTS ADICIONALES ==========
    path('passengerDetail/<int:pk>/', PassengerDetailAPIView.as_view(), name='passenger-detail'),
    path('reservationsByPassenger/<int:passenger_id>/', 
         ReservationByPassengerAPIView.as_view(), name='reservations-by-passenger'),
    
    # ========== RESERVAS - ENDPOINTS ADICIONALES ==========
    path('createReservation/', 
         CreateReservationAPIView.as_view({'post': 'create'}), name='create-reservation'),
    path('changeReservationStatus/<int:reservation_id>/', 
         ChangeReservationStatusAPIView.as_view(), name='change-reservation-status'),
    
    # ========== BOLETOS - ENDPOINTS ADICIONALES ==========
    path('generateTicket/<int:reservation_id>/', 
         GenerateTicketAPIView.as_view(), name='generate-ticket'),
    path('ticketInformation/<str:barcode>/', 
         TicketInformationAPIView.as_view(), name='ticket-information'),
    
    # ========== REPORTES ==========
#     path('passengersByFlight/<int:flight_id>/', 
#          PassengersByFlightAPIView.as_view(), name='passengers-by-flight'),
#     path('activeReservations/<int:passenger_id>/', 
#          ActiveReservationsByPassengerAPIView.as_view(), name='active-reservations'),
    path('reportes/pasajeros-vuelo/<int:vuelo_id>/', 
         PasajerosPorVueloView.as_view(), name='reporte-pasajeros-vuelo'),
    path('reportes/reservas-activas/<int:pasajero_id>/', 
         ReservasActivasPasajeroView.as_view(), name='reporte-reservas-activas'),
    
    # ========== VIEWSETS (CRUD COMPLETO) ==========
    path('', include(router.urls)),
]
