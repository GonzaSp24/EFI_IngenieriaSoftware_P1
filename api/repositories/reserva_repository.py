"""
Repository para Reservas y Boletos
"""
from reservas.models import Reserva, Boleto
from django.db.models import Q


class ReservaRepository:
    """Repository para operaciones con Reservas"""
    
    @staticmethod
    def get_all():
        """Obtener todas las reservas"""
        return Reserva.objects.select_related('vuelo', 'pasajero', 'asiento').all()
    
    @staticmethod
    def get_by_id(reserva_id):
        """Obtener una reserva por ID"""
        return Reserva.objects.select_related('vuelo', 'pasajero', 'asiento').filter(id=reserva_id).first()
    
    @staticmethod
    def get_by_codigo(codigo_reserva):
        """Obtener una reserva por código"""
        return Reserva.objects.select_related('vuelo', 'pasajero', 'asiento').filter(codigo_reserva=codigo_reserva).first()
    
    @staticmethod
    def get_by_vuelo(vuelo_id):
        """Obtener todas las reservas de un vuelo"""
        return Reserva.objects.select_related('pasajero', 'asiento').filter(vuelo_id=vuelo_id)
    
    @staticmethod
    def get_by_pasajero(pasajero_id):
        """Obtener todas las reservas de un pasajero"""
        return Reserva.objects.select_related('vuelo', 'asiento').filter(pasajero_id=pasajero_id)
    
    @staticmethod
    def create(data):
        """Crear una nueva reserva"""
        return Reserva.objects.create(**data)
    
    @staticmethod
    def update(reserva_id, data):
        """Actualizar una reserva"""
        reserva = ReservaRepository.get_by_id(reserva_id)
        if reserva:
            for key, value in data.items():
                setattr(reserva, key, value)
            reserva.save()
        return reserva
    
    @staticmethod
    def cambiar_estado(reserva_id, nuevo_estado):
        """Cambiar el estado de una reserva"""
        reserva = ReservaRepository.get_by_id(reserva_id)
        if reserva:
            reserva.estado = nuevo_estado
            reserva.save()
        return reserva
    
    @staticmethod
    def delete(reserva_id):
        """Eliminar una reserva"""
        reserva = ReservaRepository.get_by_id(reserva_id)
        if reserva:
            reserva.delete()
            return True
        return False


class BoletoRepository:
    """Repository para operaciones con Boletos"""
    
    @staticmethod
    def get_all():
        """Obtener todos los boletos"""
        return Boleto.objects.select_related('reserva__vuelo', 'reserva__pasajero').all()
    
    @staticmethod
    def get_by_id(boleto_id):
        """Obtener un boleto por ID"""
        return Boleto.objects.select_related('reserva__vuelo', 'reserva__pasajero').filter(id=boleto_id).first()
    
    @staticmethod
    def get_by_codigo(codigo_barra):
        """Obtener un boleto por código de barra"""
        return Boleto.objects.select_related('reserva__vuelo', 'reserva__pasajero').filter(codigo_barra=codigo_barra).first()
    
    @staticmethod
    def get_by_reserva(reserva_id):
        """Obtener el boleto de una reserva"""
        return Boleto.objects.filter(reserva_id=reserva_id).first()
    
    @staticmethod
    def create(reserva):
        """Crear un nuevo boleto"""
        return Boleto.objects.create(reserva=reserva)
    
    @staticmethod
    def update_estado(boleto_id, nuevo_estado):
        """Actualizar el estado de un boleto"""
        boleto = BoletoRepository.get_by_id(boleto_id)
        if boleto:
            boleto.estado = nuevo_estado
            boleto.save()
        return boleto
