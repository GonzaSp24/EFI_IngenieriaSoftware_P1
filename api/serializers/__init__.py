"""
Serializers para la API REST
"""
from .vuelo_serializers import (
    AvionSerializer,
    VueloSerializer,
    VueloListSerializer,
    VueloDetailSerializer,
    AsientoSerializer,
    AsientoDisponibilidadSerializer
)
from .pasajero_serializers import (
    PasajeroSerializer,
    PasajeroCreateSerializer,
    PasajeroDetailSerializer
)
from .reserva_serializers import (
    ReservaSerializer,
    ReservaCreateSerializer,
    ReservaDetailSerializer,
    BoletoSerializer,
    BoletoGenerateSerializer
)

__all__ = [
    'AvionSerializer',
    'VueloSerializer',
    'VueloListSerializer',
    'VueloDetailSerializer',
    'AsientoSerializer',
    'AsientoDisponibilidadSerializer',
    'PasajeroSerializer',
    'PasajeroCreateSerializer',
    'PasajeroDetailSerializer',
    'ReservaSerializer',
    'ReservaCreateSerializer',
    'ReservaDetailSerializer',
    'BoletoSerializer',
    'BoletoGenerateSerializer',
]
