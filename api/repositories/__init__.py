"""
Repositories para acceso a datos
"""
from .vuelo_repository import VueloRepository, AvionRepository, AsientoRepository
from .pasajero_repository import PasajeroRepository
from .reserva_repository import ReservaRepository, BoletoRepository

__all__ = [
    'VueloRepository',
    'AvionRepository',
    'AsientoRepository',
    'PasajeroRepository',
    'ReservaRepository',
    'BoletoRepository',
]
