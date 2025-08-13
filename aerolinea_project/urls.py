"""
URL configuration for aerolinea_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

# URLs que no necesitan internacionalización
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  # Para cambio de idioma
]

# URLs con internacionalización
urlpatterns += i18n_patterns(
    path('', include('core.urls')),  # La página principal será core/home
    path('admin/', admin.site.urls),
    path('accounts/', include('home.urls')),  # URLs de autenticación
    path('vuelos/', include('vuelos.urls')),
    path('pasajeros/', include('pasajeros.urls')),
    path('reservas/', include('reservas.urls')),
    prefix_default_language=False,  # No agregar prefijo para idioma por defecto
)

# Servir archivos estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
