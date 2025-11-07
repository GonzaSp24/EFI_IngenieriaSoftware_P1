"""
Repository para Vuelos, Aviones y Asientos.
Los Repositories son la capa de acceso a datos, encapsulan las consultas a la base de datos.
"""

from airline.models import Vuelo, Avion, Asiento
from django.db.models import Q, Count
from datetime import datetime


class AvionRepository:
    """
    Repository para operaciones de base de datos con Aviones.
    Encapsula todas las consultas relacionadas con el modelo Avion.
    """

    @staticmethod
    def get_all():
        """
        Obtener todos los aviones.
        Returns: QuerySet de Avion
        """
        return Avion.objects.all()

    @staticmethod
    def get_by_id(avion_id):
        """
        Obtener un avión por su ID.

        Args:
            avion_id: ID del avión

        Returns:
            Objeto Avion o None si no existe
        """
        return Avion.objects.filter(id=avion_id).first()

    @staticmethod
    def create(data):
        """
        Crear un nuevo avión en la base de datos.

        Args:
            data: Diccionario con los datos del avión

        Returns:
            Objeto Avion creado
        """
        return Avion.objects.create(**data)

    @staticmethod
    def update(avion_id, data):
        """
        Actualizar un avión existente.

        Args:
            avion_id: ID del avión a actualizar
            data: Diccionario con los campos a actualizar

        Returns:
            Objeto Avion actualizado o None si no existe
        """
        avion = AvionRepository.get_by_id(avion_id)
        if avion:
            for key, value in data.items():
                setattr(avion, key, value)
            avion.save()
        return avion

    @staticmethod
    def delete(avion_id):
        """
        Eliminar un avión de la base de datos.

        Args:
            avion_id: ID del avión a eliminar

        Returns:
            True si se eliminó, False si no existía
        """
        avion = AvionRepository.get_by_id(avion_id)
        if avion:
            avion.delete()
            return True
        return False


class AsientoRepository:
    """
    Repository para operaciones de base de datos con Asientos.
    """

    @staticmethod
    def get_by_avion(avion_id):
        """
        Obtener todos los asientos de un avión específico.
        Los asientos se ordenan por fila y columna para facilitar la visualización.

        Args:
            avion_id: ID del avión

        Returns:
            QuerySet de Asiento ordenado
        """
        return Asiento.objects.filter(avion_id=avion_id).order_by("fila", "columna")

    @staticmethod
    def get_by_id(asiento_id):
        """
        Obtener un asiento por su ID.

        Args:
            asiento_id: ID del asiento

        Returns:
            Objeto Asiento o None si no existe
        """
        return Asiento.objects.filter(id=asiento_id).first()

    @staticmethod
    def check_disponibilidad(asiento_id, vuelo_id):
        """
        Verificar si un asiento está disponible para un vuelo.
        Un asiento está ocupado si existe una reserva confirmada para ese vuelo.

        Args:
            asiento_id: ID del asiento
            vuelo_id: ID del vuelo

        Returns:
            True si está disponible, False si está ocupado
        """
        from airline.models import Reserva

        # Buscar si existe una reserva confirmada para este asiento en este vuelo
        reserva_existente = Reserva.objects.filter(
            asiento_id=asiento_id, vuelo_id=vuelo_id, estado="confirmada"
        ).exists()

        # Si existe reserva, NO está disponible
        return not reserva_existente


class VueloRepository:
    """
    Repository para operaciones de base de datos con Vuelos.
    """

    @staticmethod
    def get_all():
        """
        Obtener todos los vuelos.
        Usa select_related para optimizar la consulta y traer el avión relacionado.

        Returns:
            QuerySet de Vuelo con avión precargado
        """
        return Vuelo.objects.select_related("avion").all()

    @staticmethod
    def get_by_id(vuelo_id):
        """
        Obtener un vuelo por su ID.

        Args:
            vuelo_id: ID del vuelo

        Returns:
            Objeto Vuelo o None si no existe
        """
        return Vuelo.objects.select_related("avion").filter(id=vuelo_id).first()

    @staticmethod
    def filter_vuelos(
        origen=None, destino=None, fecha=None, estado=None, fecha_desde=None
    ):
        """
        Filtrar vuelos por múltiples criterios.
        Todos los filtros son opcionales y se aplican solo si se proporcionan.

        Args:
            origen: Filtrar por ciudad de origen (búsqueda parcial)
            destino: Filtrar por ciudad de destino (búsqueda parcial)
            fecha: Filtrar por fecha exacta de salida
            estado: Filtrar por estado del vuelo
            fecha_desde: Filtrar vuelos desde una fecha específica

        Returns:
            QuerySet de Vuelo filtrado y ordenado por fecha_salida
        """
        queryset = Vuelo.objects.select_related("avion").all()

        # Filtro por origen (búsqueda parcial, case-insensitive)
        if origen:
            queryset = queryset.filter(origen__icontains=origen)

        # Filtro por destino (búsqueda parcial, case-insensitive)
        if destino:
            queryset = queryset.filter(destino__icontains=destino)

        # Filtro por fecha exacta
        if fecha:
            # Convertir string a datetime si es necesario
            if isinstance(fecha, str):
                try:
                    fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
                except ValueError:
                    pass
            queryset = queryset.filter(fecha_salida__date=fecha)

        # Filtro por fecha desde (para vuelos futuros)
        if fecha_desde:
            queryset = queryset.filter(fecha_salida__gte=fecha_desde)

        # Filtro por estado
        if estado:
            queryset = queryset.filter(estado=estado)

        return queryset.order_by("fecha_salida")

    @staticmethod
    def create(data):
        """
        Crear un nuevo vuelo en la base de datos.

        Args:
            data: Diccionario con los datos del vuelo

        Returns:
            Objeto Vuelo creado
        """
        return Vuelo.objects.create(**data)

    @staticmethod
    def update(vuelo_id, data):
        """
        Actualizar un vuelo existente.

        Args:
            vuelo_id: ID del vuelo a actualizar
            data: Diccionario con los campos a actualizar

        Returns:
            Objeto Vuelo actualizado o None si no existe
        """
        vuelo = VueloRepository.get_by_id(vuelo_id)
        if vuelo:
            for key, value in data.items():
                setattr(vuelo, key, value)
            vuelo.save()
        return vuelo

    @staticmethod
    def delete(vuelo_id):
        """
        Eliminar un vuelo de la base de datos.

        Args:
            vuelo_id: ID del vuelo a eliminar

        Returns:
            True si se eliminó, False si no existía
        """
        vuelo = VueloRepository.get_by_id(vuelo_id)
        if vuelo:
            vuelo.delete()
            return True
        return False

    @staticmethod
    def get_asientos_con_disponibilidad(vuelo_id):
        """
        Obtener todos los asientos del avión con su estado de disponibilidad para un vuelo.
        Usa el método del modelo Vuelo que calcula la disponibilidad.

        Args:
            vuelo_id: ID del vuelo

        Returns:
            Lista de diccionarios con información de asientos y disponibilidad
        """
        vuelo = VueloRepository.get_by_id(vuelo_id)
        if not vuelo:
            return []

        # Usar el método del modelo que ya calcula la disponibilidad
        return vuelo.get_asientos_con_estado_para_vuelo()
