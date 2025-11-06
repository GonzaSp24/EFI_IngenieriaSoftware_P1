"""
URLs para las vistas web de la aplicación airline.
Incluye las rutas para vuelos, pasajeros y reservas.
"""

from django.urls import path
from airline import views as home_views

urlpatterns = [
    # URLs de Vuelos
    path("vuelos/", home_views.lista_vuelos, name="lista_vuelos"),
    path("vuelos/<int:pk>/", home_views.detalle_vuelo, name="detalle_vuelo"),
    path(
        "vuelos/<int:pk>/reporte/",
        home_views.reporte_pasajeros_vuelo,
        name="reporte_pasajeros_vuelo",
    ),
    # URLs de Pasajeros
    path("pasajeros/mi-perfil/", home_views.mi_perfil, name="mi_perfil"),
    path(
        "pasajeros/registrar/", home_views.registrar_pasajero, name="registrar_pasajero"
    ),
    path(
        "pasajeros/editar-perfil/", home_views.editar_mi_perfil, name="editar_mi_perfil"
    ),
    path("pasajeros/lista/", home_views.lista_pasajeros, name="lista_pasajeros"),
    # URLs de Reservas
    path(
        "reservas/crear/<int:vuelo_id>/<int:asiento_id>/",
        home_views.crear_reserva,
        name="crear_reserva",
    ),
    path(
        "reservas/detalle/<str:codigo_reserva>/",
        home_views.detalle_reserva,
        name="detalle_reserva",
    ),
    path("reservas/mis-reservas/", home_views.mis_reservas, name="mis_reservas"),
]
