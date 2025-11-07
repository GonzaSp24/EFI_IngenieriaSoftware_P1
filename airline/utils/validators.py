"""
Validadores personalizados para la aplicación airline.
"""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re


def validar_dni(value):
    """
    Valida que el DNI tenga el formato correcto.

    Args:
        value (str): DNI a validar

    Raises:
        ValidationError: Si el DNI no es válido
    """
    if not value.isdigit():
        raise ValidationError(
            _("El DNI debe contener solo números."), code="invalid_dni"
        )

    if len(value) < 7 or len(value) > 8:
        raise ValidationError(
            _("El DNI debe tener entre 7 y 8 dígitos."), code="invalid_dni_length"
        )


def validar_telefono(value):
    """
    Valida que el teléfono tenga el formato correcto.

    Args:
        value (str): Teléfono a validar

    Raises:
        ValidationError: Si el teléfono no es válido
    """
    # Permitir números, espacios, guiones y paréntesis
    pattern = r"^[\d\s\-$$$$]+$"
    if not re.match(pattern, value):
        raise ValidationError(
            _(
                "El teléfono solo puede contener números, espacios, guiones y paréntesis."
            ),
            code="invalid_phone",
        )

    # Verificar longitud mínima
    digits_only = re.sub(r"\D", "", value)
    if len(digits_only) < 10:
        raise ValidationError(
            _("El teléfono debe tener al menos 10 dígitos."),
            code="invalid_phone_length",
        )


def validar_numero_vuelo(value):
    """
    Valida que el número de vuelo tenga el formato correcto.
    Formato esperado: 2 letras seguidas de 3-4 números (ej: AA123, BA1234)

    Args:
        value (str): Número de vuelo a validar

    Raises:
        ValidationError: Si el número de vuelo no es válido
    """
    pattern = r"^[A-Z]{2}\d{3,4}$"
    if not re.match(pattern, value.upper()):
        raise ValidationError(
            _(
                "El número de vuelo debe tener el formato: 2 letras + 3-4 números (ej: AA123)."
            ),
            code="invalid_flight_number",
        )


def validar_codigo_reserva(value):
    """
    Valida que el código de reserva tenga el formato correcto.

    Args:
        value (str): Código de reserva a validar

    Raises:
        ValidationError: Si el código de reserva no es válido
    """
    if len(value) != 6:
        raise ValidationError(
            _("El código de reserva debe tener 6 caracteres."),
            code="invalid_booking_code_length",
        )

    if not value.isalnum():
        raise ValidationError(
            _("El código de reserva solo puede contener letras y números."),
            code="invalid_booking_code",
        )
