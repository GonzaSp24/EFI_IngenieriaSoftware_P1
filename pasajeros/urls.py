from django.urls import path
from . import views

urlpatterns = [
    # Para usuarios normales
    path('mi-perfil/', views.mi_perfil_pasajero, name='mi_perfil_pasajero'),
    path('registrar/', views.registrar_pasajero, name='registrar_pasajero'),
    path('editar-perfil/', views.editar_mi_perfil, name='editar_mi_perfil'),
    
    # Para administradores
    path('', views.lista_pasajeros, name='lista_pasajeros'),
    path('<int:pk>/', views.detalle_pasajero, name='detalle_pasajero'),
]
