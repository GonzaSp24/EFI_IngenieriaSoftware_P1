from django.contrib import admin
from .models import Reserva, Boleto

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ['codigo_reserva', 'vuelo', 'pasajero', 'asiento', 'estado', 'fecha_reserva', 'precio']
    list_filter = ['estado', 'fecha_reserva', 'vuelo', 'pasajero']
    search_fields = ['codigo_reserva', 'pasajero__nombre', 'pasajero__apellido', 'vuelo__origen', 'vuelo__destino']
    readonly_fields = ['codigo_reserva', 'fecha_reserva']
    raw_id_fields = ['vuelo', 'pasajero', 'asiento'] # Para seleccionar fácilmente

@admin.register(Boleto)
class BoletoAdmin(admin.ModelAdmin):
    list_display = ['reserva', 'codigo_barra', 'fecha_emision', 'estado']
    list_filter = ['estado', 'fecha_emision']
    search_fields = ['codigo_barra', 'reserva__codigo_reserva', 'reserva__pasajero__nombre']
    readonly_fields = ['codigo_barra', 'fecha_emision']
