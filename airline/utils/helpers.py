"""
Funciones helper para la aplicación airline.
"""
import random
import string
from datetime import datetime, timedelta
from decimal import Decimal


def generar_codigo_reserva(length=6):
    """
    Genera un código de reserva aleatorio.
    
    Args:
        length (int): Longitud del código (default: 6)
        
    Returns:
        str: Código de reserva generado
        
    Example:
        >>> codigo = generar_codigo_reserva()
        >>> len(codigo)
        6
    """
    caracteres = string.ascii_uppercase + string.digits
    return ''.join(random.choices(caracteres, k=length))


def generar_codigo_boleto(reserva_id):
    """
    Genera un código de boleto único basado en el ID de la reserva.
    
    Args:
        reserva_id (int): ID de la reserva
        
    Returns:
        str: Código de boleto generado
        
    Example:
        >>> codigo = generar_codigo_boleto(123)
        >>> codigo.startswith('TKT')
        True
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f"TKT{reserva_id:06d}{timestamp}"


def calcular_duracion_vuelo(fecha_salida, fecha_llegada):
    """
    Calcula la duración de un vuelo en horas y minutos.
    
    Args:
        fecha_salida (datetime): Fecha y hora de salida
        fecha_llegada (datetime): Fecha y hora de llegada
        
    Returns:
        dict: Diccionario con 'horas' y 'minutos'
        
    Example:
        >>> salida = datetime(2025, 1, 1, 10, 0)
        >>> llegada = datetime(2025, 1, 1, 13, 30)
        >>> duracion = calcular_duracion_vuelo(salida, llegada)
        >>> duracion['horas']
        3
        >>> duracion['minutos']
        30
    """
    duracion = fecha_llegada - fecha_salida
    total_minutos = int(duracion.total_seconds() / 60)
    horas = total_minutos // 60
    minutos = total_minutos % 60
    
    return {
        'horas': horas,
        'minutos': minutos,
        'total_minutos': total_minutos
    }


def calcular_precio_con_descuento(precio_base, porcentaje_descuento):
    """
    Calcula el precio final aplicando un descuento.
    
    Args:
        precio_base (Decimal): Precio base del vuelo
        porcentaje_descuento (int): Porcentaje de descuento (0-100)
        
    Returns:
        Decimal: Precio final con descuento aplicado
        
    Example:
        >>> precio = Decimal('100.00')
        >>> precio_final = calcular_precio_con_descuento(precio, 20)
        >>> precio_final
        Decimal('80.00')
    """
    if porcentaje_descuento < 0 or porcentaje_descuento > 100:
        raise ValueError("El porcentaje de descuento debe estar entre 0 y 100")
    
    descuento = precio_base * Decimal(porcentaje_descuento) / Decimal(100)
    return precio_base - descuento


def formatear_numero_asiento(fila, columna):
    """
    Formatea un número de asiento a partir de fila y columna.
    
    Args:
        fila (int): Número de fila
        columna (str): Letra de columna (A-F)
        
    Returns:
        str: Número de asiento formateado
        
    Example:
        >>> formatear_numero_asiento(12, 'A')
        '12A'
    """
    return f"{fila}{columna.upper()}"


def es_vuelo_internacional(origen, destino):
    """
    Determina si un vuelo es internacional basándose en origen y destino.
    (Simplificado: asume que si origen y destino son diferentes países)
    
    Args:
        origen (str): Ciudad/país de origen
        destino (str): Ciudad/país de destino
        
    Returns:
        bool: True si es internacional, False si es nacional
    """
    # Lista simplificada de ciudades argentinas
    ciudades_argentina = [
        'Buenos Aires', 'Córdoba', 'Rosario', 'Mendoza', 
        'Tucumán', 'Salta', 'Bariloche', 'Ushuaia'
    ]
    
    origen_nacional = any(ciudad in origen for ciudad in ciudades_argentina)
    destino_nacional = any(ciudad in destino for ciudad in ciudades_argentina)
    
    # Es internacional si uno está en Argentina y el otro no
    return origen_nacional != destino_nacional
