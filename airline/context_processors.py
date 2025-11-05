"""
Context processors para la aplicación Airline.
Proveen variables globales disponibles en todos los templates.
"""
from django.conf import settings


def airline_info(request):
    """
    Agrega información general de la aerolínea al contexto de los templates.
    
    Returns:
        dict: Diccionario con información de la aerolínea
    """
    return {
        'AIRLINE_NAME': getattr(settings, 'AIRLINE_NAME', 'Sistema de Gestión de Aerolínea'),
        'AIRLINE_CODE': getattr(settings, 'AIRLINE_CODE', 'ARL'),
        'AIRLINE_SUPPORT_EMAIL': getattr(settings, 'AIRLINE_SUPPORT_EMAIL', 'support@airline.com'),
    }


def user_info(request):
    """
    Agrega información del usuario autenticado al contexto.
    
    Returns:
        dict: Diccionario con información del usuario
    """
    context = {}
    
    if request.user.is_authenticated:
        context['is_passenger'] = hasattr(request.user, 'pasajero')
        if context['is_passenger']:
            context['passenger'] = request.user.pasajero
    
    return context
