"""
Utilidades para la API REST

Este módulo contiene funciones helper y utilidades compartidas
por toda la API, incluyendo:
- Formatos de respuesta estandarizados
- Manejador de excepciones personalizado
- Funciones de validación comunes
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Manejador personalizado de excepciones para la API.
    
    Intercepta todas las excepciones de DRF y las formatea
    en un formato consistente con error=True.
    
    Args:
        exc (Exception): La excepción lanzada
        context (dict): Contexto de la petición
    
    Returns:
        Response: Respuesta formateada con el error
    
    Ejemplo de respuesta:
        {
            "error": true,
            "message": "Descripción del error",
            "details": {...}
        }
    """
    # Llamar al manejador por defecto de DRF primero
    response = exception_handler(exc, context)
    
    if response is not None:
        # Formatear la respuesta en nuestro formato estándar
        custom_response_data = {
            'error': True,
            'message': str(exc),
            'details': response.data
        }
        response.data = custom_response_data
    
    return response


def success_response(data=None, message="Operación exitosa", status_code=status.HTTP_200_OK):
    """
    Formato estándar para respuestas exitosas de la API.
    
    Todas las respuestas exitosas siguen este formato para
    mantener consistencia en toda la API.
    
    Args:
        data: Datos a retornar (puede ser dict, list, o None)
        message (str): Mensaje descriptivo de la operación
        status_code (int): Código HTTP de respuesta (default: 200)
    
    Returns:
        Response: Respuesta DRF formateada
    
    Ejemplo de uso:
        return success_response(
            data=serializer.data,
            message="Vuelo creado exitosamente",
            status_code=status.HTTP_201_CREATED
        )
    
    Ejemplo de respuesta:
        {
            "error": false,
            "message": "Operación exitosa",
            "data": {...}
        }
    """
    return Response({
        'error': False,
        'message': message,
        'data': data
    }, status=status_code)


def error_response(message="Error en la operación", details=None, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Formato estándar para respuestas de error de la API.
    
    Todas las respuestas de error siguen este formato para
    mantener consistencia en toda la API.
    
    Args:
        message (str): Mensaje descriptivo del error
        details: Detalles adicionales del error (opcional)
        status_code (int): Código HTTP de respuesta (default: 400)
    
    Returns:
        Response: Respuesta DRF formateada
    
    Ejemplo de uso:
        return error_response(
            message="El vuelo no existe",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    Ejemplo de respuesta:
        {
            "error": true,
            "message": "Error en la operación",
            "details": {...}
        }
    """
    return Response({
        'error': True,
        'message': message,
        'details': details
    }, status=status_code)
