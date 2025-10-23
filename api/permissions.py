"""
Permisos personalizados para la API
"""
from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Permiso para usuarios administradores
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permiso para el propietario del objeto o administrador
    """
    def has_object_permission(self, request, view, obj):
        # Los administradores tienen acceso completo
        if request.user.is_staff:
            return True
        
        # El propietario puede acceder a sus propios objetos
        if hasattr(obj, 'pasajero'):
            return obj.pasajero.usuario == request.user
        if hasattr(obj, 'usuario'):
            return obj.usuario == request.user
        
        return False


class ReadOnly(permissions.BasePermission):
    """
    Permiso de solo lectura
    """
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
