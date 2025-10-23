"""
URLs para la API REST
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from api.views import (
    VueloViewSet, AvionViewSet, AsientoViewSet,
    PasajeroViewSet, ReservaViewSet, BoletoViewSet,
    RegisterView, LoginView
)
from api.views.reporte_views import PasajerosPorVueloView, ReservasActivasPasajeroView

# Configuración de Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="API Sistema de Gestión de Aerolínea",
        default_version='v1',
        description="""
        API REST para el Sistema de Gestión de Aerolínea
        
        ## Autenticación
        Esta API utiliza JWT (JSON Web Tokens) para autenticación.
        
        ### Cómo usar:
        1. Registrarse en `/api/auth/register/` o iniciar sesión en `/api/auth/login/`
        2. Copiar el token de acceso (access token)
        3. Hacer clic en el botón "Authorize" arriba
        4. Ingresar: `Bearer <tu_token_aqui>`
        5. Ahora puedes usar todos los endpoints protegidos
        
        ## Endpoints principales:
        - **Vuelos**: Buscar y gestionar vuelos
        - **Pasajeros**: Registrar y gestionar pasajeros
        - **Reservas**: Crear y gestionar reservas
        - **Boletos**: Generar y consultar boletos
        - **Reportes**: Estadísticas y reportes (solo admin)
        """,
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@aerolinea.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Router para ViewSets
router = DefaultRouter()
router.register(r'vuelos', VueloViewSet, basename='vuelo')
router.register(r'aviones', AvionViewSet, basename='avion')
router.register(r'asientos', AsientoViewSet, basename='asiento')
router.register(r'pasajeros', PasajeroViewSet, basename='pasajero')
router.register(r'reservas', ReservaViewSet, basename='reserva')
router.register(r'boletos', BoletoViewSet, basename='boleto')

urlpatterns = [
    # Documentación Swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    # Autenticación
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Reportes
    path('reportes/pasajeros-por-vuelo/<int:vuelo_id>/', PasajerosPorVueloView.as_view(), name='pasajeros-por-vuelo'),
    path('reportes/reservas-activas/<int:pasajero_id>/', ReservasActivasPasajeroView.as_view(), name='reservas-activas-pasajero'),
    
    # Router URLs
    path('', include(router.urls)),
]
