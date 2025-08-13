from django.urls import path
from . import views

urlpatterns = [
    path('crear/<int:vuelo_id>/<int:asiento_id>/', views.crear_reserva, name='crear_reserva'),
    path('detalle/<str:codigo_reserva>/', views.detalle_reserva, name='detalle_reserva'),
    path('boleto/<str:codigo_reserva>/', views.generar_boleto, name='generar_boleto'),
    path('mis-reservas/', views.mis_reservas, name='mis_reservas'),
    path('cancelar/<int:pk>/', views.cancelar_reserva, name='cancelar_reserva'),
    # Nuevas URLs para PDF y email
    path('descargar-pdf/<str:codigo_reserva>/', views.descargar_boleto_pdf, name='descargar_boleto_pdf'),
    path('reenviar-email/<str:codigo_reserva>/', views.reenviar_boleto_email, name='reenviar_boleto_email'),
]
