"""
Views para la API REST
"""
from .vuelo_views import VueloViewSet, AvionViewSet, AsientoViewSet
from .pasajero_views import PasajeroViewSet
from .reserva_views import ReservaViewSet, BoletoViewSet
from .auth_views import RegisterView, LoginView

__all__ = [
    'VueloViewSet',
    'AvionViewSet',
    'AsientoViewSet',
    'PasajeroViewSet',
    'ReservaViewSet',
    'BoletoViewSet',
    'RegisterView',
    'LoginView',
]
