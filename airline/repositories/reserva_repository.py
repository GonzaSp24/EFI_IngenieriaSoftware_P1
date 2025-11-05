"""
Repository para Reservas y Boletos

Este módulo contiene las capas de acceso a datos para los modelos
Reserva y Boleto. Encapsula todas las consultas a la base de datos
relacionadas con el sistema de reservas y emisión de boletos.
"""
from airline.models import Reserva, Boleto
from django.db.models import Q


class ReservaRepository:
    """
    Repository para operaciones con Reservas
    
    Proporciona métodos para realizar operaciones CRUD y consultas
    específicas sobre el modelo Reserva. Utiliza select_related para
    optimizar las consultas y evitar el problema N+1.
    """
    
    @staticmethod
    def get_all():
        """
        Obtener todas las reservas con sus relaciones cargadas
        
        Utiliza select_related para cargar vuelo, pasajero y asiento
        en una sola consulta SQL, mejorando el rendimiento.
        
        Returns:
            QuerySet: QuerySet con todas las reservas
        """
        return Reserva.objects.select_related('vuelo', 'pasajero', 'asiento').all()
    
    @staticmethod
    def get_by_id(reserva_id):
        """
        Buscar una reserva por su ID con relaciones cargadas
        
        Args:
            reserva_id (int): ID de la reserva
            
        Returns:
            Reserva|None: Objeto reserva si existe, None si no se encuentra
        """
        return Reserva.objects.select_related('vuelo', 'pasajero', 'asiento').filter(id=reserva_id).first()
    
    @staticmethod
    def get_by_codigo(codigo_reserva):
        """
        Buscar una reserva por su código único
        
        El código de reserva es generado automáticamente y debe ser único.
        
        Args:
            codigo_reserva (str): Código único de la reserva
            
        Returns:
            Reserva|None: Objeto reserva si existe, None si no se encuentra
        """
        return Reserva.objects.select_related('vuelo', 'pasajero', 'asiento').filter(codigo_reserva=codigo_reserva).first()
    
    @staticmethod
    def get_by_vuelo(vuelo_id):
        """
        Obtener todas las reservas de un vuelo específico
        
        Args:
            vuelo_id (int): ID del vuelo
            
        Returns:
            QuerySet: QuerySet con las reservas del vuelo
        """
        return Reserva.objects.select_related('pasajero', 'asiento').filter(vuelo_id=vuelo_id)
    
    @staticmethod
    def get_by_pasajero(pasajero_id):
        """
        Obtener todas las reservas de un pasajero específico
        
        Args:
            pasajero_id (int): ID del pasajero
            
        Returns:
            QuerySet: QuerySet con las reservas del pasajero
        """
        return Reserva.objects.select_related('vuelo', 'asiento').filter(pasajero_id=pasajero_id)
    
    @staticmethod
    def create(data):
        """
        Crear una nueva reserva en la base de datos
        
        Args:
            data (dict): Diccionario con los datos de la reserva
                        (vuelo, pasajero, asiento, estado, etc.)
            
        Returns:
            Reserva: Objeto reserva creado
        """
        return Reserva.objects.create(**data)
    
    @staticmethod
    def update(reserva_id, data):
        """
        Actualizar los datos de una reserva existente
        
        Args:
            reserva_id (int): ID de la reserva a actualizar
            data (dict): Diccionario con los campos a actualizar
            
        Returns:
            Reserva|None: Objeto reserva actualizado, None si no existe
        """
        reserva = ReservaRepository.get_by_id(reserva_id)
        if reserva:
            for key, value in data.items():
                setattr(reserva, key, value)
            reserva.save()
        return reserva
    
    @staticmethod
    def cambiar_estado(reserva_id, nuevo_estado):
        """
        Cambiar el estado de una reserva
        
        Estados válidos: 'pendiente', 'confirmada', 'cancelada'
        
        Args:
            reserva_id (int): ID de la reserva
            nuevo_estado (str): Nuevo estado de la reserva
            
        Returns:
            Reserva|None: Objeto reserva actualizado, None si no existe
        """
        reserva = ReservaRepository.get_by_id(reserva_id)
        if reserva:
            reserva.estado = nuevo_estado
            reserva.save()
        return reserva
    
    @staticmethod
    def delete(reserva_id):
        """
        Eliminar una reserva de la base de datos
        
        Args:
            reserva_id (int): ID de la reserva a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False si no existe
        """
        reserva = ReservaRepository.get_by_id(reserva_id)
        if reserva:
            reserva.delete()
            return True
        return False


class BoletoRepository:
    """
    Repository para operaciones con Boletos
    
    Proporciona métodos para realizar operaciones sobre el modelo Boleto.
    Los boletos están vinculados a reservas confirmadas y tienen su propio
    ciclo de vida.
    """
    
    @staticmethod
    def get_all():
        """
        Obtener todos los boletos con sus relaciones cargadas
        
        Utiliza select_related para cargar la reserva y sus relaciones
        (vuelo, pasajero) en una sola consulta SQL.
        
        Returns:
            QuerySet: QuerySet con todos los boletos
        """
        return Boleto.objects.select_related('reserva__vuelo', 'reserva__pasajero').all()
    
    @staticmethod
    def get_by_id(boleto_id):
        """
        Buscar un boleto por su ID con relaciones cargadas
        
        Args:
            boleto_id (int): ID del boleto
            
        Returns:
            Boleto|None: Objeto boleto si existe, None si no se encuentra
        """
        return Boleto.objects.select_related('reserva__vuelo', 'reserva__pasajero').filter(id=boleto_id).first()
    
    @staticmethod
    def get_by_codigo(codigo_barra):
        """
        Buscar un boleto por su código de barra único
        
        El código de barra es generado automáticamente al crear el boleto.
        
        Args:
            codigo_barra (str): Código de barra del boleto
            
        Returns:
            Boleto|None: Objeto boleto si existe, None si no se encuentra
        """
        return Boleto.objects.select_related('reserva__vuelo', 'reserva__pasajero').filter(codigo_barra=codigo_barra).first()
    
    @staticmethod
    def get_by_reserva(reserva_id):
        """
        Obtener el boleto asociado a una reserva
        
        Cada reserva puede tener un único boleto.
        
        Args:
            reserva_id (int): ID de la reserva
            
        Returns:
            Boleto|None: Objeto boleto si existe, None si no se encuentra
        """
        return Boleto.objects.filter(reserva_id=reserva_id).first()
    
    @staticmethod
    def create(reserva):
        """
        Crear un nuevo boleto para una reserva
        
        El código de barra se genera automáticamente en el modelo.
        El estado inicial es 'emitido'.
        
        Args:
            reserva (Reserva): Objeto reserva para la cual crear el boleto
            
        Returns:
            Boleto: Objeto boleto creado
        """
        return Boleto.objects.create(reserva=reserva)
    
    @staticmethod
    def update_estado(boleto_id, nuevo_estado):
        """
        Actualizar el estado de un boleto
        
        Estados válidos: 'emitido', 'usado', 'anulado'
        
        Args:
            boleto_id (int): ID del boleto
            nuevo_estado (str): Nuevo estado del boleto
            
        Returns:
            Boleto|None: Objeto boleto actualizado, None si no existe
        """
        boleto = BoletoRepository.get_by_id(boleto_id)
        if boleto:
            boleto.estado = nuevo_estado
            boleto.save()
        return boleto
