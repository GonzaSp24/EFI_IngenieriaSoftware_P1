from django.conf import settings
from rest_framework.permissions import BasePermission


class TokenPermission(BasePermission):
    """
    Permiso personalizado basado en token Bearer.
    Verifica que el request tenga un header Authorization con formato: Bearer <token>
    
    El token debe estar en la lista VALID_TOKENS del settings.py
    """
    message = "Token no válido o no proporcionado"

    def has_permission(self, request, view):
        # Obtener el header Authorization
        auth_header = request.META.get("HTTP_AUTHORIZATION", None)
        
        # Verificar que exista y tenga el formato correcto
        if not auth_header or not auth_header.startswith("Bearer "):
            return False
        
        # Extraer el token
        token = auth_header.split(" ", 1)[1].strip()
        
        # Verificar que el token esté en la lista de tokens válidos
        valid_tokens = getattr(settings, 'VALID_TOKENS', [])
        return token in valid_tokens

    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj)


class IsAdminUser(BasePermission):
    """
    Permiso para verificar que el usuario sea administrador (staff).
    """
    message = "Solo los administradores pueden realizar esta acción"
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff


class IsOwnerOrAdmin(BasePermission):
    """
    Permiso que permite acceso al propietario del objeto o a un administrador.
    
    Verifica:
    - Si el usuario es admin (is_staff), permite acceso
    - Si el objeto tiene relación con el usuario (pasajero.usuario o usuario), permite acceso
    """
    message = "No tienes permiso para acceder a este recurso"
    
    def has_object_permission(self, request, view, obj):
        # Los administradores tienen acceso completo
        if request.user.is_staff:
            return True
        
        # Verificar si el objeto tiene relación con el usuario
        # Para objetos con campo 'pasajero' (como Reserva)
        if hasattr(obj, 'pasajero') and hasattr(obj.pasajero, 'usuario'):
            return obj.pasajero.usuario == request.user
        
        # Para objetos con campo 'usuario' directo
        if hasattr(obj, 'usuario'):
            return obj.usuario == request.user
        
        return False
