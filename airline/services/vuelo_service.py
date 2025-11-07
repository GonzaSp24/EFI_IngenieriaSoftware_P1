"""
Services para lógica de negocio de Vuelos, Aviones y Asientos.
Los Services actúan como capa intermedia entre las Views y los Repositories,
conteniendo la lógica de negocio y validaciones.
"""

from airline.repositories import VueloRepository, AvionRepository, AsientoRepository
from rest_framework.exceptions import ValidationError, NotFound
from datetime import timedelta


class AvionService:
    """
    Service para lógica de negocio de Aviones.
    Maneja operaciones CRUD y validaciones relacionadas con aviones.
    """

    @staticmethod
    def get_all_aviones():
        """
        Obtener todos los aviones registrados.
        Retorna: QuerySet de Avion
        """
        return AvionRepository.get_all()

    @staticmethod
    def get_avion(avion_id):
        """
        Obtener un avión específico por su ID.

        Args:
            avion_id: ID del avión a buscar

        Returns:
            Objeto Avion

        Raises:
            NotFound: Si el avión no existe
        """
        avion = AvionRepository.get_by_id(avion_id)
        if not avion:
            raise NotFound("Avión no encontrado")
        return avion

    @staticmethod
    def create_avion(data=None, /, **kwargs):
        """
        Acepta un dict (data) o kwargs (modelo=..., capacidad=..., etc.)
        y siempre delega al repositorio con un dict.
        """
        if data is None:
            data = kwargs
        payload = dict(data or {})
        return AvionRepository.create(payload)

    @staticmethod
    def update_avion(avion_id, data=None, /, **kwargs):
        """
        Igual que create_avion, pero para update.
        """
        if data is None:
            data = kwargs
        payload = dict(data or {})
        return AvionRepository.update(avion_id, payload)

    @staticmethod
    def delete_avion(avion_id):
        """
        Eliminar un avión.

        Args:
            avion_id: ID del avión a eliminar

        Returns:
            True si se eliminó correctamente

        Raises:
            NotFound: Si el avión no existe
        """
        success = AvionRepository.delete(avion_id)
        if not success:
            raise NotFound("Avión no encontrado")
        return success


class AsientoService:
    """
    Service para lógica de negocio de Asientos.
    Maneja consultas y validaciones de disponibilidad de asientos.
    """

    @staticmethod
    def get_asientos_by_avion(avion_id):
        """
        Obtener todos los asientos de un avión específico.

        Args:
            avion_id: ID del avión

        Returns:
            QuerySet de Asiento ordenados por fila y columna

        Raises:
            NotFound: Si el avión no existe
        """
        avion = AvionRepository.get_by_id(avion_id)
        if not avion:
            raise NotFound("Avión no encontrado")
        return AsientoRepository.get_by_avion(avion_id)

    @staticmethod
    def check_disponibilidad(asiento_id, vuelo_id):
        """
        Verificar si un asiento está disponible para un vuelo específico.
        Un asiento está disponible si no tiene una reserva confirmada para ese vuelo.

        Args:
            asiento_id: ID del asiento
            vuelo_id: ID del vuelo

        Returns:
            True si está disponible, False si está ocupado

        Raises:
            NotFound: Si el asiento o vuelo no existen
        """
        asiento = AsientoRepository.get_by_id(asiento_id)
        if not asiento:
            raise NotFound("Asiento no encontrado")

        vuelo = VueloRepository.get_by_id(vuelo_id)
        if not vuelo:
            raise NotFound("Vuelo no encontrado")

        return AsientoRepository.check_disponibilidad(asiento_id, vuelo_id)


class VueloService:
    """
    Service para lógica de negocio de Vuelos.
    Maneja operaciones CRUD, filtros y validaciones de vuelos.
    """

    @staticmethod
    def get_all_vuelos():
        """
        Obtener todos los vuelos registrados.
        Incluye información del avión relacionado (select_related).

        Returns:
            QuerySet de Vuelo
        """
        return VueloRepository.get_all()

    @staticmethod
    def get_vuelo(vuelo_id):
        """
        Obtener un vuelo específico por su ID.

        Args:
            vuelo_id: ID del vuelo a buscar

        Returns:
            Objeto Vuelo

        Raises:
            NotFound: Si el vuelo no existe
        """
        vuelo = VueloRepository.get_by_id(vuelo_id)
        if not vuelo:
            raise NotFound("Vuelo no encontrado")
        return vuelo.objects.get(pk=vuelo_id)

    @staticmethod
    def get_upcoming_flights():
        """
        Obtener vuelos futuros (fecha de salida mayor a hoy).
        Útil para mostrar vuelos disponibles para reservar.

        Returns:
            QuerySet de Vuelo con fecha_salida > hoy
        """
        from django.utils import timezone

        return VueloRepository.filter_vuelos(fecha_desde=timezone.now())

    @staticmethod
    def filter_vuelos(origen=None, destino=None, fecha=None, estado=None):
        """
        Filtrar vuelos por múltiples criterios.
        Todos los parámetros son opcionales.

        Args:
            origen: Ciudad de origen (búsqueda parcial, case-insensitive)
            destino: Ciudad de destino (búsqueda parcial, case-insensitive)
            fecha: Fecha de salida (formato YYYY-MM-DD)
            estado: Estado del vuelo (programado, en_curso, etc.)

        Returns:
            QuerySet de Vuelo filtrado y ordenado por fecha_salida
        """
        return VueloRepository.filter_vuelos(origen, destino, fecha, estado)

    @staticmethod
    def create_vuelo(*, origen, destino, fecha_salida, fecha_llegada, precio_base, estado, avion_id):
        """
        Crear un nuevo vuelo.
        Valida que el avión exista antes de crear el vuelo.

        Args:
            data: Diccionario con los datos del vuelo

        Returns:
            Objeto Vuelo creado

        Raises:
            ValidationError: Si el avión no existe o datos inválidos
        """
        # Validaciones básicas
        if fecha_llegada <= fecha_salida:
            raise ValueError("fecha_llegada debe ser posterior a fecha_salida")

        duracion = fecha_llegada - fecha_salida  # <-- calcular acá

        data = {
            "origen": origen,
            "destino": destino,
            "fecha_salida": fecha_salida,
            "fecha_llegada": fecha_llegada,
            "duracion": duracion,
            "precio_base": precio_base,
            "estado": estado,
            "avion_id": avion_id,
        }
        # Usá tu repo o el modelo directamente
        return VueloRepository.create(data)  # o Vuelo.objects.create(**data)

    @staticmethod
    def update_vuelo(*, vuelo_id, origen=None, destino=None, fecha_salida=None, fecha_llegada=None,
                         precio_base=None, estado=None, avion_id=None):
        """
        Actualizar un vuelo existente.

        Args:
            vuelo_id: ID del vuelo a actualizar
            data: Diccionario con los datos a actualizar

        Returns:
            Objeto Vuelo actualizado

        Raises:
            NotFound: Si el vuelo no existe
        """
        vuelo = VueloRepository.get_by_id(vuelo_id) 

        # Aplicar cambios
        if origen is not None: vuelo.origen = origen
        if destino is not None: vuelo.destino = destino
        if fecha_salida is not None: vuelo.fecha_salida = fecha_salida
        if fecha_llegada is not None: vuelo.fecha_llegada = fecha_llegada
        if precio_base is not None: vuelo.precio_base = precio_base
        if estado is not None: vuelo.estado = estado
        if avion_id is not None: vuelo.avion_id = avion_id

        # Recalcular duración si cambió alguna fecha
        if vuelo.fecha_salida and vuelo.fecha_llegada:
            if vuelo.fecha_llegada <= vuelo.fecha_salida:
                raise ValueError("fecha_llegada debe ser posterior a fecha_salida")
            vuelo.duracion = vuelo.fecha_llegada - vuelo.fecha_salida

        VueloRepository.save(vuelo) 
        return vuelo

    @staticmethod
    def delete_vuelo(vuelo_id):
        """
        Eliminar un vuelo.
        Valida que no tenga reservas confirmadas antes de eliminar.

        Args:
            vuelo_id: ID del vuelo a eliminar

        Returns:
            True si se eliminó correctamente

        Raises:
            ValidationError: Si el vuelo tiene reservas confirmadas
            NotFound: Si el vuelo no existe
        """
        # Verificar que no tenga reservas confirmadas
        from airline.repositories import ReservaRepository

        reservas = ReservaRepository.get_by_vuelo(vuelo_id)
        if reservas.filter(estado="confirmada").exists():
            raise ValidationError(
                "No se puede eliminar un vuelo con reservas confirmadas"
            )

        success = VueloRepository.delete(vuelo_id)
        if not success:
            raise NotFound("Vuelo no encontrado")
        return success

    @staticmethod
    def get_asientos_disponibles(vuelo_id):
        """
        Obtener asientos con su disponibilidad para un vuelo específico.
        Retorna información detallada de cada asiento y si está ocupado o disponible.

        Args:
            vuelo_id: ID del vuelo

        Returns:
            Lista de diccionarios con información de asientos y su disponibilidad

        Raises:
            NotFound: Si el vuelo no existe
        """
        vuelo = VueloRepository.get_by_id(vuelo_id)
        if not vuelo:
            raise NotFound("Vuelo no encontrado")

        return VueloRepository.get_asientos_con_disponibilidad(vuelo_id)
