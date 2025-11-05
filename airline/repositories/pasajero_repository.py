"""
Repository para Pasajeros

Este módulo contiene la capa de acceso a datos para el modelo Pasajero.
Los repositories encapsulan todas las consultas a la base de datos,
proporcionando una interfaz limpia para que los services interactúen
con los datos sin conocer los detalles de implementación de Django ORM.
"""
from airline.models import Pasajero
from django.db.models import Q


class PasajeroRepository:
    """
    Repository para operaciones con Pasajeros
    
    Proporciona métodos para realizar operaciones CRUD y consultas
    específicas sobre el modelo Pasajero. Todos los métodos son estáticos
    ya que no mantienen estado.
    """
    
    @staticmethod
    def get_all():
        """
        Obtener todos los pasajeros de la base de datos
        
        Returns:
            QuerySet: QuerySet con todos los pasajeros
        """
        return Pasajero.objects.all()
    
    @staticmethod
    def get_by_id(pasajero_id):
        """
        Buscar un pasajero por su ID (clave primaria)
        
        Args:
            pasajero_id (int): ID del pasajero
            
        Returns:
            Pasajero|None: Objeto pasajero si existe, None si no se encuentra
        """
        return Pasajero.objects.filter(id=pasajero_id).first()
    
    @staticmethod
    def get_by_documento(documento):
        """
        Buscar un pasajero por su número de documento
        
        El documento debe ser único en el sistema.
        
        Args:
            documento (str): Número de documento del pasajero
            
        Returns:
            Pasajero|None: Objeto pasajero si existe, None si no se encuentra
        """
        return Pasajero.objects.filter(documento=documento).first()
    
    @staticmethod
    def get_by_email(email):
        """
        Buscar un pasajero por su dirección de email
        
        El email debe ser único en el sistema.
        
        Args:
            email (str): Email del pasajero
            
        Returns:
            Pasajero|None: Objeto pasajero si existe, None si no se encuentra
        """
        return Pasajero.objects.filter(email=email).first()
    
    @staticmethod
    def get_by_usuario(usuario):
        """
        Buscar un pasajero asociado a un usuario del sistema
        
        Args:
            usuario (User): Objeto usuario de Django
            
        Returns:
            Pasajero|None: Objeto pasajero si existe, None si no se encuentra
        """
        return Pasajero.objects.filter(usuario=usuario).first()
    
    @staticmethod
    def create(data):
        """
        Crear un nuevo registro de pasajero en la base de datos
        
        Args:
            data (dict): Diccionario con los datos del pasajero
                        (nombre, apellido, documento, email, etc.)
            
        Returns:
            Pasajero: Objeto pasajero creado
        """
        return Pasajero.objects.create(**data)
    
    @staticmethod
    def update(pasajero_id, data):
        """
        Actualizar los datos de un pasajero existente
        
        Busca el pasajero por ID y actualiza solo los campos
        proporcionados en el diccionario data.
        
        Args:
            pasajero_id (int): ID del pasajero a actualizar
            data (dict): Diccionario con los campos a actualizar
            
        Returns:
            Pasajero|None: Objeto pasajero actualizado, None si no existe
        """
        pasajero = PasajeroRepository.get_by_id(pasajero_id)
        if pasajero:
            for key, value in data.items():
                setattr(pasajero, key, value)
            pasajero.save()
        return pasajero
    
    @staticmethod
    def delete(pasajero_id):
        """
        Eliminar un pasajero de la base de datos
        
        Args:
            pasajero_id (int): ID del pasajero a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False si no existe
        """
        pasajero = PasajeroRepository.get_by_id(pasajero_id)
        if pasajero:
            pasajero.delete()
            return True
        return False
    
    @staticmethod
    def get_reservas(pasajero_id):
        """
        Obtener todas las reservas de un pasajero
        
        Utiliza select_related para optimizar la consulta y cargar
        las relaciones de vuelo y asiento en una sola query.
        
        Args:
            pasajero_id (int): ID del pasajero
            
        Returns:
            QuerySet|list: QuerySet con las reservas o lista vacía si no existe el pasajero
        """
        pasajero = PasajeroRepository.get_by_id(pasajero_id)
        if pasajero:
            return pasajero.reservas.select_related('vuelo', 'asiento').all()
        return []
    
    @staticmethod
    def get_reservas_activas(pasajero_id):
        """
        Obtener solo las reservas activas (confirmadas) de un pasajero
        
        Filtra las reservas por estado 'confirmada' y optimiza la consulta
        con select_related.
        
        Args:
            pasajero_id (int): ID del pasajero
            
        Returns:
            QuerySet|list: QuerySet con las reservas activas o lista vacía
        """
        pasajero = PasajeroRepository.get_by_id(pasajero_id)
        if pasajero:
            return pasajero.reservas.filter(estado='confirmada').select_related('vuelo', 'asiento').all()
        return []
