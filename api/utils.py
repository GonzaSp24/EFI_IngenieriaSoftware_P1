"""
Utilidades para la API REST
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Manejador personalizado de excepciones para la API
    """
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response_data = {
            'error': True,
            'message': str(exc),
            'details': response.data
        }
        response.data = custom_response_data
    
    return response


def success_response(data=None, message="Operación exitosa", status_code=status.HTTP_200_OK):
    """
    Formato estándar para respuestas exitosas
    """
    return Response({
        'error': False,
        'message': message,
        'data': data
    }, status=status_code)


def error_response(message="Error en la operación", details=None, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Formato estándar para respuestas de error
    """
    return Response({
        'error': True,
        'message': message,
        'details': details
    }, status=status_code)
