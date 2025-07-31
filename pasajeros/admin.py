from django.contrib import admin
from .models import Pasajero

@admin.register(Pasajero)
class PasajeroAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'apellido', 'documento', 'email', 'telefono', 'fecha_nacimiento']
    list_filter = ['tipo_documento']
    search_fields = ['nombre', 'apellido', 'documento', 'email']
    ordering = ['apellido', 'nombre']
