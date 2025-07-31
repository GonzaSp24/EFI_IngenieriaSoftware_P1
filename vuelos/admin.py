from django.contrib import admin
from .models import Avion, Vuelo, Asiento

@admin.register(Avion)
class AvionAdmin(admin.ModelAdmin):
    list_display = ['modelo', 'capacidad', 'filas', 'columnas']
    list_filter = ['modelo']
    search_fields = ['modelo']
    readonly_fields = ['capacidad'] # Capacidad se calcula por filas*columnas

    def save_model(self, request, obj, form, change):
        # Recalcular capacidad antes de guardar si filas/columnas cambian
        obj.capacidad = obj.filas * obj.columnas
        super().save_model(request, obj, form, change)

@admin.register(Vuelo)
class VueloAdmin(admin.ModelAdmin):
    list_display = ['origen', 'destino', 'fecha_salida', 'fecha_llegada', 'estado', 'precio_base', 'avion', 'asientos_disponibles_count']
    list_filter = ['estado', 'origen', 'destino', 'fecha_salida', 'avion']
    search_fields = ['origen', 'destino', 'avion__modelo']
    date_hierarchy = 'fecha_salida'
    raw_id_fields = ['avion'] # Para seleccionar aviones más fácilmente si hay muchos

@admin.register(Asiento)
class AsientoAdmin(admin.ModelAdmin):
    list_display = ['numero', 'avion', 'fila', 'columna', 'tipo', 'estado']
    list_filter = ['tipo', 'estado', 'avion']
    search_fields = ['numero', 'avion__modelo']
    readonly_fields = ['numero', 'fila', 'columna'] # Estos campos se generan automáticamente
