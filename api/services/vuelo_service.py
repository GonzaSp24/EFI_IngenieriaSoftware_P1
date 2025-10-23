"""
Services para lógica de negocio de Vuelos
"""
from api.repositories import VueloRepository, AvionRepository, AsientoRepository
from rest_framework.exceptions import ValidationError, NotFound


class AvionService:
    """Service para lógica de negocio de Aviones"""
    
    @staticmethod
    def get_all_aviones():
        """Obtener todos los aviones"""
        return AvionRepository.get_all()
    
    @staticmethod
    def get_avion(avion_id):
        """Obtener un avión por ID"""
        avion = AvionRepository.get_by_id(avion_id)
        if not avion:
            raise NotFound("Avión no encontrado")
        return avion
    
    @staticmethod
    def create_avion(data):
        """Crear un nuevo avión"""
        return AvionRepository.create(data)
    
    @staticmethod
    def update_avion(avion_id, data):
        """Actualizar un avión"""
        avion = AvionRepository.update(avion_id, data)
        if not avion:
            raise NotFound("Avión no encontrado")
        return avion
    
    @staticmethod
    def delete_avion(avion_id):
        """Eliminar un avión"""
        success = AvionRepository.delete(avion_id)
        if not success:
            raise NotFound("Avión no encontrado")
        return success


class AsientoService:
    """Service para lógica de negocio de Asientos"""
    
    @staticmethod
    def get_asientos_by_avion(avion_id):
        """Obtener asientos de un avión"""
        avion = AvionRepository.get_by_id(avion_id)
        if not avion:
            raise NotFound("Avión no encontrado")
        return AsientoRepository.get_by_avion(avion_id)
    
    @staticmethod
    def check_disponibilidad(asiento_id, vuelo_id):
        """Verificar disponibilidad de un asiento para un vuelo"""
        asiento = AsientoRepository.get_by_id(asiento_id)
        if not asiento:
            raise NotFound("Asiento no encontrado")
        
        vuelo = VueloRepository.get_by_id(vuelo_id)
        if not vuelo:
            raise NotFound("Vuelo no encontrado")
        
        return AsientoRepository.check_disponibilidad(asiento_id, vuelo_id)


class VueloService:
    """Service para lógica de negocio de Vuelos"""
    
    @staticmethod
    def get_all_vuelos():
        """Obtener todos los vuelos"""
        return VueloRepository.get_all()
    
    @staticmethod
    def get_vuelo(vuelo_id):
        """Obtener un vuelo por ID"""
        vuelo = VueloRepository.get_by_id(vuelo_id)
        if not vuelo:
            raise NotFound("Vuelo no encontrado")
        return vuelo
    
    @staticmethod
    def filter_vuelos(origen=None, destino=None, fecha=None, estado=None):
        """Filtrar vuelos por criterios"""
        return VueloRepository.filter_vuelos(origen, destino, fecha, estado)
    
    @staticmethod
    def create_vuelo(data):
        """Crear un nuevo vuelo"""
        # Validar que el avión exista
        avion = AvionRepository.get_by_id(data.get('avion_id'))
        if not avion:
            raise ValidationError("El avión especificado no existe")
        
        return VueloRepository.create(data)
    
    @staticmethod
    def update_vuelo(vuelo_id, data):
        """Actualizar un vuelo"""
        vuelo = VueloRepository.update(vuelo_id, data)
        if not vuelo:
            raise NotFound("Vuelo no encontrado")
        return vuelo
    
    @staticmethod
    def delete_vuelo(vuelo_id):
        """Eliminar un vuelo"""
        # Verificar que no tenga reservas confirmadas
        from api.repositories import ReservaRepository
        reservas = ReservaRepository.get_by_vuelo(vuelo_id)
        if reservas.filter(estado='confirmada').exists():
            raise ValidationError(
                "No se puede eliminar un vuelo con reservas confirmadas"
            )
        
        success = VueloRepository.delete(vuelo_id)
        if not success:
            raise NotFound("Vuelo no encontrado")
        return success
    
    @staticmethod
    def get_asientos_disponibles(vuelo_id):
        """Obtener asientos con disponibilidad para un vuelo"""
        vuelo = VueloRepository.get_by_id(vuelo_id)
        if not vuelo:
            raise NotFound("Vuelo no encontrado")
        
        return VueloRepository.get_asientos_con_disponibilidad(vuelo_id)
