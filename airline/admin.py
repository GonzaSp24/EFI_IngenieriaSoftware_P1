"""
Configuración del panel de administración de Django para los modelos de Airline.
"""
from django.contrib import admin
from .models import Avion, Vuelo, Asiento, Pasajero, Reserva, Boleto


@admin.register(Avion)
class AvionAdmin(admin.ModelAdmin):
    list_display = ('modelo', 'capacidad', 'filas', 'columnas')
    search_fields = ('modelo',)


@admin.register(Vuelo)
class VueloAdmin(admin.ModelAdmin):
    list_display = ('origen', 'destino', 'fecha_salida', 'fecha_llegada', 'estado', 'precio_base')
    list_filter = ('estado', 'origen', 'destino')
    search_fields = ('origen', 'destino')
    date_hierarchy = 'fecha_salida'


@admin.register(Asiento)
class AsientoAdmin(admin.ModelAdmin):
    list_display = ('numero', 'avion', 'tipo', 'estado', 'fila', 'columna')
    list_filter = ('tipo', 'estado', 'avion')
    search_fields = ('numero',)


@admin.register(Pasajero)
class PasajeroAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'documento', 'email', 'telefono')
    search_fields = ('nombre', 'apellido', 'documento', 'email')


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('codigo_reserva', 'vuelo', 'pasajero', 'asiento', 'estado', 'fecha_reserva', 'precio')
    list_filter = ('estado', 'fecha_reserva')
    search_fields = ('codigo_reserva', 'pasajero__nombre', 'pasajero__apellido')
    date_hierarchy = 'fecha_reserva'


@admin.register(Boleto)
class BoletoAdmin(admin.ModelAdmin):
    list_display = ('codigo_barra', 'reserva', 'estado', 'fecha_emision')
    list_filter = ('estado', 'fecha_emision')
    search_fields = ('codigo_barra', 'reserva__codigo_reserva')
    date_hierarchy = 'fecha_emision'
