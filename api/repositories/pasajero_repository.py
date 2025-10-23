"""
Repository para Pasajeros
"""
from pasajeros.models import Pasajero
from django.db.models import Q


class PasajeroRepository:
    """Repository para operaciones con Pasajeros"""
    
    @staticmethod
    def get_all():
        """Obtener todos los pasajeros"""
        return Pasajero.objects.all()
    
    @staticmethod
    def get_by_id(pasajero_id):
        """Obtener un pasajero por ID"""
        return Pasajero.objects.filter(id=pasajero_id).first()
    
    @staticmethod
    def get_by_documento(documento):
        """Obtener un pasajero por documento"""
        return Pasajero.objects.filter(documento=documento).first()
    
    @staticmethod
    def get_by_email(email):
        """Obtener un pasajero por email"""
        return Pasajero.objects.filter(email=email).first()
    
    @staticmethod
    def get_by_usuario(usuario):
        """Obtener un pasajero por usuario"""
        return Pasajero.objects.filter(usuario=usuario).first()
    
    @staticmethod
    def create(data):
        """Crear un nuevo pasajero"""
        return Pasajero.objects.create(**data)
    
    @staticmethod
    def update(pasajero_id, data):
        """Actualizar un pasajero"""
        pasajero = PasajeroRepository.get_by_id(pasajero_id)
        if pasajero:
            for key, value in data.items():
                setattr(pasajero, key, value)
            pasajero.save()
        return pasajero
    
    @staticmethod
    def delete(pasajero_id):
        """Eliminar un pasajero"""
        pasajero = PasajeroRepository.get_by_id(pasajero_id)
        if pasajero:
            pasajero.delete()
            return True
        return False
    
    @staticmethod
    def get_reservas(pasajero_id):
        """Obtener todas las reservas de un pasajero"""
        pasajero = PasajeroRepository.get_by_id(pasajero_id)
        if pasajero:
            return pasajero.reservas.select_related('vuelo', 'asiento').all()
        return []
    
    @staticmethod
    def get_reservas_activas(pasajero_id):
        """Obtener reservas activas de un pasajero"""
        pasajero = PasajeroRepository.get_by_id(pasajero_id)
        if pasajero:
            return pasajero.reservas.filter(estado='confirmada').select_related('vuelo', 'asiento').all()
        return []
