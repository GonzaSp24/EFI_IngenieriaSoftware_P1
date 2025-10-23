"""
Repository para Vuelos, Aviones y Asientos
"""
from vuelos.models import Vuelo, Avion, Asiento
from django.db.models import Q, Count
from datetime import datetime


class AvionRepository:
    """Repository para operaciones con Aviones"""
    
    @staticmethod
    def get_all():
        """Obtener todos los aviones"""
        return Avion.objects.all()
    
    @staticmethod
    def get_by_id(avion_id):
        """Obtener un avión por ID"""
        return Avion.objects.filter(id=avion_id).first()
    
    @staticmethod
    def create(data):
        """Crear un nuevo avión"""
        return Avion.objects.create(**data)
    
    @staticmethod
    def update(avion_id, data):
        """Actualizar un avión"""
        avion = AvionRepository.get_by_id(avion_id)
        if avion:
            for key, value in data.items():
                setattr(avion, key, value)
            avion.save()
        return avion
    
    @staticmethod
    def delete(avion_id):
        """Eliminar un avión"""
        avion = AvionRepository.get_by_id(avion_id)
        if avion:
            avion.delete()
            return True
        return False


class AsientoRepository:
    """Repository para operaciones con Asientos"""
    
    @staticmethod
    def get_by_avion(avion_id):
        """Obtener todos los asientos de un avión"""
        return Asiento.objects.filter(avion_id=avion_id).order_by('fila', 'columna')
    
    @staticmethod
    def get_by_id(asiento_id):
        """Obtener un asiento por ID"""
        return Asiento.objects.filter(id=asiento_id).first()
    
    @staticmethod
    def check_disponibilidad(asiento_id, vuelo_id):
        """Verificar si un asiento está disponible para un vuelo"""
        from reservas.models import Reserva
        
        reserva_existente = Reserva.objects.filter(
            asiento_id=asiento_id,
            vuelo_id=vuelo_id,
            estado='confirmada'
        ).exists()
        
        return not reserva_existente


class VueloRepository:
    """Repository para operaciones con Vuelos"""
    
    @staticmethod
    def get_all():
        """Obtener todos los vuelos"""
        return Vuelo.objects.select_related('avion').all()
    
    @staticmethod
    def get_by_id(vuelo_id):
        """Obtener un vuelo por ID"""
        return Vuelo.objects.select_related('avion').filter(id=vuelo_id).first()
    
    @staticmethod
    def filter_vuelos(origen=None, destino=None, fecha=None, estado=None):
        """Filtrar vuelos por criterios"""
        queryset = Vuelo.objects.select_related('avion').all()
        
        if origen:
            queryset = queryset.filter(origen__icontains=origen)
        
        if destino:
            queryset = queryset.filter(destino__icontains=destino)
        
        if fecha:
            # Convertir string a datetime si es necesario
            if isinstance(fecha, str):
                try:
                    fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
                except ValueError:
                    pass
            queryset = queryset.filter(fecha_salida__date=fecha)
        
        if estado:
            queryset = queryset.filter(estado=estado)
        
        return queryset.order_by('fecha_salida')
    
    @staticmethod
    def create(data):
        """Crear un nuevo vuelo"""
        return Vuelo.objects.create(**data)
    
    @staticmethod
    def update(vuelo_id, data):
        """Actualizar un vuelo"""
        vuelo = VueloRepository.get_by_id(vuelo_id)
        if vuelo:
            for key, value in data.items():
                setattr(vuelo, key, value)
            vuelo.save()
        return vuelo
    
    @staticmethod
    def delete(vuelo_id):
        """Eliminar un vuelo"""
        vuelo = VueloRepository.get_by_id(vuelo_id)
        if vuelo:
            vuelo.delete()
            return True
        return False
    
    @staticmethod
    def get_asientos_con_disponibilidad(vuelo_id):
        """Obtener asientos con su disponibilidad para un vuelo"""
        vuelo = VueloRepository.get_by_id(vuelo_id)
        if not vuelo:
            return []
        
        return vuelo.get_asientos_con_estado_para_vuelo()
