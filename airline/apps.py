from django.apps import AppConfig


class AirlineConfig(AppConfig):
    """
    Configuración de la aplicación Airline.
    Esta es la aplicación principal que contiene toda la lógica de negocio
    del sistema de gestión de aerolínea.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'airline'
    verbose_name = 'Sistema de Aerolínea'
