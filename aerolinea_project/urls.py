"""aerolinea_project URL Configuration"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # URLs principales de la aerolínea
    path('vuelos/', include('vuelos.urls')),
    path('pasajeros/', include('pasajeros.urls')),
    path('reservas/', include('reservas.urls')),
    
    # Usar tu sistema de autenticación existente
    path('accounts/', include('home.urls')),  # Tu app home para login/register
]
