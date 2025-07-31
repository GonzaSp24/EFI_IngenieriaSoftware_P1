from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_pasajeros, name='lista_pasajeros'),
    path('registrar/', views.registrar_pasajero, name='registrar_pasajero'),
    path('<int:pk>/', views.detalle_pasajero, name='detalle_pasajero'),
    path('<int:pk>/historial/', views.historial_vuelos_pasajero, name='historial_vuelos_pasajero'),
]
