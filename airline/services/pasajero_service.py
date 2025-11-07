"""
Services para lógica de negocio de Pasajeros

Este módulo contiene la capa de servicios que maneja toda la lógica de negocio
relacionada con los pasajeros. Los servicios actúan como intermediarios entre
las vistas (API) y los repositorios (acceso a datos), aplicando validaciones
y reglas de negocio antes de interactuar con la base de datos.
"""

from airline.repositories import PasajeroRepository
from rest_framework.exceptions import ValidationError, NotFound
from datetime import date
from rest_framework.exceptions import ValidationError
from airline.models import Pasajero


class PasajeroService:
    """
    Service para lógica de negocio de Pasajeros

    Esta clase contiene métodos estáticos que implementan las reglas de negocio
    para la gestión de pasajeros. Cada método valida los datos y delega las
    operaciones de base de datos al PasajeroRepository.
    """

    @staticmethod
    def get_all_pasajeros():
        """
        Obtener todos los pasajeros registrados en el sistema

        Returns:
            QuerySet: Lista de todos los pasajeros
        """
        return PasajeroRepository.get_all()

    @staticmethod
    def get_pasajero(pasajero_id):
        """
        Obtener un pasajero específico por su ID

        Args:
            pasajero_id (int): ID del pasajero a buscar

        Returns:
            Pasajero: Objeto pasajero encontrado

        Raises:
            NotFound: Si el pasajero no existe
        """
        pasajero = PasajeroRepository.get_by_id(pasajero_id)
        if not pasajero:
            raise NotFound("Pasajero no encontrado")
        return pasajero

    @staticmethod
    def get_pasajero_by_documento(documento):
        """
        Obtener un pasajero por su número de documento

        Args:
            documento (str): Número de documento del pasajero

        Returns:
            Pasajero: Objeto pasajero encontrado

        Raises:
            NotFound: Si no existe un pasajero con ese documento
        """
        pasajero = PasajeroRepository.get_by_documento(documento)
        if not pasajero:
            raise NotFound("Pasajero no encontrado")
        return pasajero

    @staticmethod
    def create_pasajero(data=None, /, **kwargs):
        """
        Crear un pasajero aceptando un dict (data) o kwargs.
        Siempre retorna una instancia de `Pasajero`.
        """
        # 1) Unificar entrada
        if data is None:
            data = kwargs
        # defensivo: trabajar sobre una copia
        payload = dict(data or {})

        # 2) Normalizaciones/por defecto
        # fecha_nacimiento puede venir como string "YYYY-MM-DD" o vacío
        fn = payload.get("fecha_nacimiento")
        if isinstance(fn, str) and fn.strip():
            try:
                payload["fecha_nacimiento"] = date.fromisoformat(fn)
            except ValueError:
                raise ValidationError("fecha_nacimiento debe tener formato YYYY-MM-DD")
        elif not fn:
            payload["fecha_nacimiento"] = None

        # telefono opcional
        payload.setdefault("telefono", "")

        # 3) Validaciones de unicidad
        if PasajeroRepository.get_by_documento(payload.get("documento")):
            raise ValidationError("Ya existe un pasajero con este documento")
        if PasajeroRepository.get_by_email(payload.get("email")):
            raise ValidationError("Ya existe un pasajero con este email")

        # 4) Crear (el repo debe crear el registro)
        obj = PasajeroRepository.create(payload)

        # 5) Asegurar que devolvemos un modelo, no un dict
        if isinstance(obj, dict):
            # si el repo devolvió un dict con id, re-hidratar
            if obj.get("id"):
                obj = Pasajero.objects.get(id=obj["id"])
            else:
                # fallback por email (único)
                obj = Pasajero.objects.get(email=payload["email"])

        # 6) Vincular usuario si vino en payload (opcional)
        usuario = payload.get("usuario")
        if usuario and getattr(obj, "usuario_id", None) is None:
            obj.usuario = usuario
            obj.save(update_fields=["usuario"])

        return obj

    @staticmethod
    def update_pasajero(pasajero_id, data):
        """
        Actualizar los datos de un pasajero existente

        Args:
            pasajero_id (int): ID del pasajero a actualizar
            data (dict): Datos a actualizar

        Returns:
            Pasajero: Objeto pasajero actualizado

        Raises:
            NotFound: Si el pasajero no existe
        """
        pasajero = PasajeroRepository.update(pasajero_id, data)
        if not pasajero:
            raise NotFound("Pasajero no encontrado")
        return pasajero

    @staticmethod
    def delete_pasajero(pasajero_id):
        """
        Eliminar un pasajero del sistema

        Valida que el pasajero no tenga reservas activas antes de eliminarlo.
        Esta es una regla de negocio importante para mantener la integridad
        de los datos.

        Args:
            pasajero_id (int): ID del pasajero a eliminar

        Returns:
            bool: True si se eliminó correctamente

        Raises:
            ValidationError: Si el pasajero tiene reservas activas
            NotFound: Si el pasajero no existe
        """
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
        """
        Obtener todas las reservas de un pasajero (activas, canceladas, etc.)

        Args:
            pasajero_id (int): ID del pasajero

        Returns:
            QuerySet: Lista de reservas del pasajero

        Raises:
            NotFound: Si el pasajero no existe
        """
        pasajero = PasajeroRepository.get_by_id(pasajero_id)
        if not pasajero:
            raise NotFound("Pasajero no encontrado")
        return PasajeroRepository.get_reservas(pasajero_id)

    @staticmethod
    def get_reservas_activas_pasajero(pasajero_id):
        """
        Obtener solo las reservas activas (confirmadas) de un pasajero

        Args:
            pasajero_id (int): ID del pasajero

        Returns:
            QuerySet: Lista de reservas activas del pasajero

        Raises:
            NotFound: Si el pasajero no existe
        """
        pasajero = PasajeroRepository.get_by_id(pasajero_id)
        if not pasajero:
            raise NotFound("Pasajero no encontrado")
        return PasajeroRepository.get_reservas_activas(pasajero_id)
