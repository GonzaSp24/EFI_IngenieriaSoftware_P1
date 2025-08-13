from django.contrib import admin
from .models import Pasajero

@admin.register(Pasajero)
class PasajeroAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'apellido', 'documento', 'tipo_documento', 'email', 'telefono', 'fecha_nacimiento', 'edad']
    list_filter = ['tipo_documento']
    search_fields = ['nombre', 'apellido', 'documento', 'email']
    date_hierarchy = 'fecha_nacimiento'
    
    def edad(self, obj):
        return obj.edad()
    edad.short_description = 'Edad'
