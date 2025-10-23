"""
Services para lógica de negocio de Pasajeros
"""
from api.repositories import PasajeroRepository
from rest_framework.exceptions import ValidationError, NotFound


class PasajeroService:
    """Service para lógica de negocio de Pasajeros"""
    
    @staticmethod
    def get_all_pasajeros():
        """Obtener todos los pasajeros"""
        return PasajeroRepository.get_all()
    
    @staticmethod
    def get_pasajero(pasajero_id):
        """Obtener un pasajero por ID"""
        pasajero = PasajeroRepository.get_by_id(pasajero_id)
        if not pasajero:
            raise NotFound("Pasajero no encontrado")
        return pasajero
    
    @staticmethod
    def get_pasajero_by_documento(documento):
        """Obtener un pasajero por documento"""
        pasajero = PasajeroRepository.get_by_documento(documento)
        if not pasajero:
            raise NotFound("Pasajero no encontrado")
        return pasajero
    
    @staticmethod
    def create_pasajero(data):
        """Crear un nuevo pasajero"""
        # Validar que no exista el documento
        if PasajeroRepository.get_by_documento(data.get('documento')):
            raise ValidationError("Ya existe un pasajero con este documento")
        
        # Validar que no exista el email
        if PasajeroRepository.get_by_email(data.get('email')):
            raise ValidationError("Ya existe un pasajero con este email")
        
        return PasajeroRepository.create(data)
    
    @staticmethod
    def update_pasajero(pasajero_id, data):
        """Actualizar un pasajero"""
        pasajero = PasajeroRepository.update(pasajero_id, data)
        if not pasajero:
            raise NotFound("Pasajero no encontrado")
        return pasajero
    
    @staticmethod
    def delete_pasajero(pasajero_id):
        """Eliminar un pasajero"""
        # Verificar que no tenga reservas activas
        reservas_activas = PasajeroRepository.get_reservas_activas(pasajero_id)
        if reservas_activas:
            raise ValidationError(
                "No se puede eliminar un pasajero con reservas activas"
            )
        
        success = PasajeroRepository.delete(pasajero_id)
        if not success:
            raise NotFound("Pasajero no encontrado")
        return success
    
    @staticmethod
    def get_reservas_pasajero(pasajero_id):
        """Obtener todas las reservas de un pasajero"""
        pasajero = PasajeroRepository.get_by_id(pasajero_id)
        if not pasajero:
            raise NotFound("Pasajero no encontrado")
        return PasajeroRepository.get_reservas(pasajero_id)
    
    @staticmethod
    def get_reservas_activas_pasajero(pasajero_id):
        """Obtener reservas activas de un pasajero"""
        pasajero = PasajeroRepository.get_by_id(pasajero_id)
        if not pasajero:
            raise NotFound("Pasajero no encontrado")
        return PasajeroRepository.get_reservas_activas(pasajero_id)
