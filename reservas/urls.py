from django.urls import path
from . import views

urlpatterns = [
    path('crear/<int:vuelo_id>/<int:asiento_id>/', views.crear_reserva, name='crear_reserva'),
    path('mis-reservas/', views.mis_reservas, name='mis_reservas'),
    path('<str:codigo_reserva>/', views.detalle_reserva, name='detalle_reserva'),
    path('<str:codigo_reserva>/boleto/', views.generar_boleto, name='generar_boleto'),
    path('cancelar/<str:codigo_reserva>/', views.cancelar_reserva, name='cancelar_reserva'),
]
