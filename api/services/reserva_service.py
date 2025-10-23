"""
Services para lógica de negocio de Reservas y Boletos
"""
from api.repositories import ReservaRepository, BoletoRepository, VueloRepository, PasajeroRepository, AsientoRepository
from rest_framework.exceptions import ValidationError, NotFound


class ReservaService:
    """Service para lógica de negocio de Reservas"""
    
    @staticmethod
    def get_all_reservas():
        """Obtener todas las reservas"""
        return ReservaRepository.get_all()
    
    @staticmethod
    def get_reserva(reserva_id):
        """Obtener una reserva por ID"""
        reserva = ReservaRepository.get_by_id(reserva_id)
        if not reserva:
            raise NotFound("Reserva no encontrada")
        return reserva
    
    @staticmethod
    def get_reserva_by_codigo(codigo_reserva):
        """Obtener una reserva por código"""
        reserva = ReservaRepository.get_by_codigo(codigo_reserva)
        if not reserva:
            raise NotFound("Reserva no encontrada")
        return reserva
    
    @staticmethod
    def create_reserva(data):
        """Crear una nueva reserva con validaciones"""
        vuelo_id = data.get('vuelo').id if hasattr(data.get('vuelo'), 'id') else data.get('vuelo')
        pasajero_id = data.get('pasajero').id if hasattr(data.get('pasajero'), 'id') else data.get('pasajero')
        asiento_id = data.get('asiento').id if hasattr(data.get('asiento'), 'id') else data.get('asiento')
        
        # Validar que el vuelo exista
        vuelo = VueloRepository.get_by_id(vuelo_id)
        if not vuelo:
            raise ValidationError("El vuelo especificado no existe")
        
        # Validar que el pasajero exista
        pasajero = PasajeroRepository.get_by_id(pasajero_id)
        if not pasajero:
            raise ValidationError("El pasajero especificado no existe")
        
        # Validar que el asiento exista
        asiento = AsientoRepository.get_by_id(asiento_id)
        if not asiento:
            raise ValidationError("El asiento especificado no existe")
        
        # Validar que el asiento pertenezca al avión del vuelo
        if asiento.avion_id != vuelo.avion_id:
            raise ValidationError("El asiento no pertenece al avión de este vuelo")
        
        # Validar que el asiento esté disponible
        if not AsientoRepository.check_disponibilidad(asiento_id, vuelo_id):
            raise ValidationError("El asiento ya está reservado para este vuelo")
        
        # Validar que el pasajero no tenga ya una reserva para este vuelo
        reservas_existentes = ReservaRepository.get_by_vuelo(vuelo_id).filter(
            pasajero_id=pasajero_id
        ).exclude(estado='cancelada')
        
        if reservas_existentes.exists():
            raise ValidationError("El pasajero ya tiene una reserva para este vuelo")
        
        # Crear la reserva con estado pendiente por defecto
        if 'estado' not in data:
            data['estado'] = 'pendiente'
        
        return ReservaRepository.create(data)
    
    @staticmethod
    def confirmar_reserva(reserva_id):
        """Confirmar una reserva"""
        reserva = ReservaRepository.get_by_id(reserva_id)
        if not reserva:
            raise NotFound("Reserva no encontrada")
        
        if reserva.estado == 'confirmada':
            raise ValidationError("La reserva ya está confirmada")
        
        if reserva.estado == 'cancelada':
            raise ValidationError("No se puede confirmar una reserva cancelada")
        
        return ReservaRepository.cambiar_estado(reserva_id, 'confirmada')
    
    @staticmethod
    def cancelar_reserva(reserva_id):
        """Cancelar una reserva"""
        reserva = ReservaRepository.get_by_id(reserva_id)
        if not reserva:
            raise NotFound("Reserva no encontrada")
        
        if reserva.estado == 'cancelada':
            raise ValidationError("La reserva ya está cancelada")
        
        # Si tiene boleto, anularlo
        if hasattr(reserva, 'boleto'):
            BoletoService.anular_boleto(reserva.boleto.id)
        
        return ReservaRepository.cambiar_estado(reserva_id, 'cancelada')
    
    @staticmethod
    def update_reserva(reserva_id, data):
        """Actualizar una reserva"""
        reserva = ReservaRepository.update(reserva_id, data)
        if not reserva:
            raise NotFound("Reserva no encontrada")
        return reserva


class BoletoService:
    """Service para lógica de negocio de Boletos"""
    
    @staticmethod
    def get_all_boletos():
        """Obtener todos los boletos"""
        return BoletoRepository.get_all()
    
    @staticmethod
    def get_boleto(boleto_id):
        """Obtener un boleto por ID"""
        boleto = BoletoRepository.get_by_id(boleto_id)
        if not boleto:
            raise NotFound("Boleto no encontrado")
        return boleto
    
    @staticmethod
    def get_boleto_by_codigo(codigo_barra):
        """Obtener un boleto por código de barra"""
        boleto = BoletoRepository.get_by_codigo(codigo_barra)
        if not boleto:
            raise NotFound("Boleto no encontrado")
        return boleto
    
    @staticmethod
    def generar_boleto(reserva_id):
        """Generar un boleto para una reserva"""
        reserva = ReservaRepository.get_by_id(reserva_id)
        if not reserva:
            raise NotFound("Reserva no encontrada")
        
        if reserva.estado != 'confirmada':
            raise ValidationError("Solo se pueden generar boletos para reservas confirmadas")
        
        # Verificar que no tenga ya un boleto
        if hasattr(reserva, 'boleto'):
            raise ValidationError("Esta reserva ya tiene un boleto generado")
        
        return BoletoRepository.create(reserva)
    
    @staticmethod
    def anular_boleto(boleto_id):
        """Anular un boleto"""
        boleto = BoletoRepository.get_by_id(boleto_id)
        if not boleto:
            raise NotFound("Boleto no encontrado")
        
        if boleto.estado == 'anulado':
            raise ValidationError("El boleto ya está anulado")
        
        return BoletoRepository.update_estado(boleto_id, 'anulado')
    
    @staticmethod
    def marcar_boleto_usado(boleto_id):
        """Marcar un boleto como usado"""
        boleto = BoletoRepository.get_by_id(boleto_id)
        if not boleto:
            raise NotFound("Boleto no encontrado")
        
        if boleto.estado == 'usado':
            raise ValidationError("El boleto ya fue usado")
        
        if boleto.estado == 'anulado':
            raise ValidationError("No se puede usar un boleto anulado")
        
        return BoletoRepository.update_estado(boleto_id, 'usado')
