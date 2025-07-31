"""aerolinea_project URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core.views import home # Importa la vista home de tu app 'core'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'), # Tu página de inicio
    
    # Incluye las URLs de tus aplicaciones
    path('vuelos/', include('vuelos.urls')),
    path('pasajeros/', include('pasajeros.urls')),
    path('reservas/', include('reservas.urls')),
    path('usuarios/', include('usuarios.urls')), # Para el registro de usuarios
    
    # URLs de Autenticación (Django's built-in)
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    # La URL de registro se manejará en la app 'usuarios'
]
