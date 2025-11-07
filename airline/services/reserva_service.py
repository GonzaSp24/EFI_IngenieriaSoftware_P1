"""
Services para lógica de negocio de Reservas y Boletos

Este módulo contiene las capas de servicios para reservas y boletos.
Implementa todas las reglas de negocio complejas como validación de
disponibilidad de asientos, estados de reservas, generación de boletos, etc.
"""
from django.db import transaction
from airline.repositories import (
    ReservaRepository,
    BoletoRepository,
    VueloRepository,
    PasajeroRepository,
    AsientoRepository,
)
from airline.models import Vuelo, Pasajero, Asiento, Reserva,  User
from rest_framework.exceptions import ValidationError, NotFound


class ReservaService:
    """
    Service para lógica de negocio de Reservas

    Maneja toda la lógica relacionada con la creación, modificación y
    cancelación de reservas. Incluye validaciones complejas de disponibilidad
    y reglas de negocio específicas del sistema de reservas.
    """

    @staticmethod
    def get_all_reservas():
        """
        Obtener todas las reservas del sistema

        Returns:
            QuerySet: Lista de todas las reservas con sus relaciones cargadas
        """
        return ReservaRepository.get_all()

    @staticmethod
    def get_reserva(reserva_id):
        """
        Obtener una reserva específica por su ID

        Args:
            reserva_id (int): ID de la reserva

        Returns:
            Reserva: Objeto reserva encontrado

        Raises:
            NotFound: Si la reserva no existe
        """
        reserva = ReservaRepository.get_by_id(reserva_id)
        if not reserva:
            raise NotFound("Reserva no encontrada")
        return reserva

    @staticmethod
    def get_reserva_by_codigo(codigo_reserva):
        """
        Obtener una reserva por su código único

        Args:
            codigo_reserva (str): Código único de la reserva

        Returns:
            Reserva: Objeto reserva encontrado

        Raises:
            NotFound: Si no existe una reserva con ese código
        """
        reserva = ReservaRepository.get_by_codigo(codigo_reserva)
        if not reserva:
            raise NotFound("Reserva no encontrada")
        return reserva

    @staticmethod
    @transaction.atomic
    def create_reserva(
        *,
        vuelo=None, vuelo_id=None,
        pasajero=None, pasajero_id=None,
        asiento=None, asiento_id=None,
        codigo_reserva=None,
        precio=None,
        estado="pendiente"
    ) -> Reserva:
        # Resolver objetos a partir de IDs si hace falta
        if vuelo is None:
            if vuelo_id is None:
                raise ValidationError({"vuelo": "Debe indicar 'vuelo' o 'vuelo_id'."})
            try:
                vuelo = Vuelo.objects.get(pk=vuelo_id)
            except Vuelo.DoesNotExist:
                raise NotFound("Vuelo no encontrado")

        if pasajero is None:
            if pasajero_id is None:
                raise ValidationError({"pasajero": "Debe indicar 'pasajero' o 'pasajero_id'."})
            try:
                pasajero = Pasajero.objects.get(pk=pasajero_id)
            except Pasajero.DoesNotExist:
                raise NotFound("Pasajero no encontrado")

        if asiento is None:
            if asiento_id is None:
                raise ValidationError({"asiento": "Debe indicar 'asiento' o 'asiento_id'."})
            try:
                asiento = Asiento.objects.get(pk=asiento_id)
            except Asiento.DoesNotExist:
                raise NotFound("Asiento no encontrado")

        # Validaciones de negocio
        if asiento.avion_id != vuelo.avion_id:
            raise ValidationError({"asiento": "El asiento no pertenece al avión de este vuelo."})

        if Reserva.objects.filter(vuelo=vuelo, asiento=asiento, estado="confirmada").exists():
            raise ValidationError({"asiento": "El asiento ya está reservado para este vuelo."})

        # Precio por defecto desde el vuelo
        if precio is None:
            precio = vuelo.precio_base

        # Crear
        reserva = Reserva.objects.create(
            vuelo=vuelo,
            pasajero=pasajero,
            asiento=asiento,
            codigo_reserva=codigo_reserva,
            precio=precio,
            estado=estado,
        )
        return reserva

    @staticmethod
    def confirmar_reserva(reserva_id):
        """
        Confirmar una reserva pendiente

        Cambia el estado de la reserva a 'confirmada'. Solo se pueden
        confirmar reservas en estado 'pendiente'.

        Args:
            reserva_id (int): ID de la reserva a confirmar

        Returns:
            Reserva: Objeto reserva actualizado

        Raises:
            NotFound: Si la reserva no existe
            ValidationError: Si la reserva ya está confirmada o cancelada
        """
        reserva = ReservaRepository.get_by_id(reserva_id)
        if not reserva:
            raise NotFound("Reserva no encontrada")

        if reserva.estado == "confirmada":
            raise ValidationError("La reserva ya está confirmada")

        if reserva.estado == "cancelada":
            raise ValidationError("No se puede confirmar una reserva cancelada")

        return ReservaRepository.cambiar_estado(reserva_id, "confirmada")

    @staticmethod
    def cancelar_reserva(reserva_id):
        """
        Cancelar una reserva existente

        Cambia el estado de la reserva a 'cancelada'. Si la reserva tiene
        un boleto asociado, también lo anula automáticamente.

        Args:
            reserva_id (int): ID de la reserva a cancelar

        Returns:
            Reserva: Objeto reserva actualizado

        Raises:
            NotFound: Si la reserva no existe
            ValidationError: Si la reserva ya está cancelada
        """
        reserva = ReservaRepository.get_by_id(reserva_id)
        if not reserva:
            raise NotFound("Reserva no encontrada")

        if reserva.estado == "cancelada":
            raise ValidationError("La reserva ya está cancelada")

        # Si tiene boleto asociado, anularlo automáticamente
        if hasattr(reserva, "boleto"):
            BoletoService.anular_boleto(reserva.boleto.id)

        return ReservaRepository.cambiar_estado(reserva_id, "cancelada")

    @staticmethod
    @transaction.atomic
    def update_reserva(
        *,
        reserva_id: int,
        estado=None,
        asiento=None, asiento_id=None,
        precio=None
    ) -> Reserva:
        try:
            reserva = Reserva.objects.select_for_update().get(pk=reserva_id)
        except Reserva.DoesNotExist:
            raise NotFound("Reserva no encontrada")

        # Cambiar asiento (opcional)
        if asiento is None and asiento_id is not None:
            try:
                asiento = Asiento.objects.get(pk=asiento_id)
            except Asiento.DoesNotExist:
                raise NotFound("Asiento no encontrado")

        if asiento is not None:
            if asiento.avion_id != reserva.vuelo.avion_id:
                raise ValidationError({"asiento": "El asiento no pertenece al avión del vuelo."})
            if Reserva.objects.filter(
                vuelo=reserva.vuelo, asiento=asiento, estado="confirmada"
            ).exclude(pk=reserva.pk).exists():
                raise ValidationError({"asiento": "El asiento ya está reservado para este vuelo."})
            reserva.asiento = asiento

        if estado is not None:
            reserva.estado = estado

        if precio is not None:
            reserva.precio = precio

        reserva.save()
        return reserva


class BoletoService:
    """
    Service para lógica de negocio de Boletos

    Maneja la generación, anulación y uso de boletos. Los boletos son
    generados a partir de reservas confirmadas y tienen su propio ciclo
    de vida (emitido -> usado/anulado).
    """

    @staticmethod
    def get_all_boletos():
        """
        Obtener todos los boletos del sistema

        Returns:
            QuerySet: Lista de todos los boletos con sus relaciones cargadas
        """
        return BoletoRepository.get_all()

    @staticmethod
    def get_boleto(boleto_id):
        """
        Obtener un boleto específico por su ID

        Args:
            boleto_id (int): ID del boleto

        Returns:
            Boleto: Objeto boleto encontrado

        Raises:
            NotFound: Si el boleto no existe
        """
        boleto = BoletoRepository.get_by_id(boleto_id)
        if not boleto:
            raise NotFound("Boleto no encontrado")
        return boleto

    @staticmethod
    def get_boleto_by_codigo(codigo_barra):
        """
        Obtener un boleto por su código de barra único

        Args:
            codigo_barra (str): Código de barra del boleto

        Returns:
            Boleto: Objeto boleto encontrado

        Raises:
            NotFound: Si no existe un boleto con ese código
        """
        boleto = BoletoRepository.get_by_codigo(codigo_barra)
        if not boleto:
            raise NotFound("Boleto no encontrado")
        return boleto

    @staticmethod
    def create_boleto(reserva_id):
        """
        Generar un boleto para una reserva confirmada

        Solo se pueden generar boletos para reservas en estado 'confirmada'.
        Cada reserva puede tener un único boleto asociado.

        Args:
            reserva_id (int): ID de la reserva para la cual generar el boleto

        Returns:
            Boleto: Objeto boleto creado con código de barra único

        Raises:
            NotFound: Si la reserva no existe
            ValidationError: Si la reserva no está confirmada o ya tiene boleto
        """
        reserva = ReservaRepository.get_by_id(reserva_id)
        if not reserva:
            raise NotFound("Reserva no encontrada")

        if reserva.estado != "confirmada":
            raise ValidationError(
                "Solo se pueden generar boletos para reservas confirmadas"
            )

        # Verificar que no tenga ya un boleto generado
        if hasattr(reserva, "boleto"):
            raise ValidationError("Esta reserva ya tiene un boleto generado")

        return BoletoRepository.create(reserva)

    @staticmethod
    def anular_boleto(boleto_id):
        """
        Anular un boleto emitido

        Cambia el estado del boleto a 'anulado'. Los boletos anulados
        no pueden ser utilizados.

        Args:
            boleto_id (int): ID del boleto a anular

        Returns:
            Boleto: Objeto boleto actualizado

        Raises:
            NotFound: Si el boleto no existe
            ValidationError: Si el boleto ya está anulado
        """
        boleto = BoletoRepository.get_by_id(boleto_id)
        if not boleto:
            raise NotFound("Boleto no encontrado")

        if boleto.estado == "anulado":
            raise ValidationError("El boleto ya está anulado")

        return BoletoRepository.update_estado(boleto_id, "anulado")

    @staticmethod
    def marcar_boleto_usado(boleto_id):
        """
        Marcar un boleto como usado (check-in realizado)

        Cambia el estado del boleto a 'usado'. Solo se pueden usar
        boletos en estado 'emitido'.

        Args:
            boleto_id (int): ID del boleto a marcar como usado

        Returns:
            Boleto: Objeto boleto actualizado

        Raises:
            NotFound: Si el boleto no existe
            ValidationError: Si el boleto ya fue usado o está anulado
        """
        boleto = BoletoRepository.get_by_id(boleto_id)
        if not boleto:
            raise NotFound("Boleto no encontrado")

        if boleto.estado == "usado":
            raise ValidationError("El boleto ya fue usado")

        if boleto.estado == "anulado":
            raise ValidationError("No se puede usar un boleto anulado")

        return BoletoRepository.update_estado(boleto_id, "usado")
