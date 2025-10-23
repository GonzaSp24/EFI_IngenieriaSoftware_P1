"""
Views para Pasajeros
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_yasg.utils import swagger_auto_schema

from api.serializers import (
    PasajeroSerializer, PasajeroCreateSerializer, PasajeroDetailSerializer,
    ReservaDetailSerializer
)
from api.services import PasajeroService
from api.permissions import IsAdminUser, IsOwnerOrAdmin
from api.utils import success_response, error_response


class PasajeroViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Pasajeros
    
    list: Listar pasajeros (solo admin)
    retrieve: Obtener detalle de un pasajero
    create: Registrar un nuevo pasajero
    update: Actualizar un pasajero
    destroy: Eliminar un pasajero (solo admin)
    reservas: Obtener reservas de un pasajero
    reservas_activas: Obtener reservas activas de un pasajero
    """
    
    def get_permissions(self):
        """Permisos según la acción"""
        if self.action == 'create':
            return [AllowAny()]
        elif self.action in ['list', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated(), IsOwnerOrAdmin()]
    
    def get_serializer_class(self):
        """Serializer según la acción"""
        if self.action == 'create':
            return PasajeroCreateSerializer
        elif self.action == 'retrieve':
            return PasajeroDetailSerializer
        return PasajeroSerializer
    
    def list(self, request):
        """Listar todos los pasajeros"""
        pasajeros = PasajeroService.get_all_pasajeros()
        serializer = PasajeroSerializer(pasajeros, many=True)
        return success_response(serializer.data, "Pasajeros obtenidos exitosamente")
    
    def retrieve(self, request, pk=None):
        """Obtener detalle de un pasajero"""
        try:
            pasajero = PasajeroService.get_pasajero(pk)
            self.check_object_permissions(request, pasajero)
            serializer = self.get_serializer_class()(pasajero)
            return success_response(serializer.data, "Pasajero obtenido exitosamente")
        except Exception as e:
            return error_response(str(e), status_code=status.HTTP_404_NOT_FOUND)
    
    def create(self, request):
        """Registrar un nuevo pasajero"""
        serializer = self.get_serializer_class()(data=request.data)
        if serializer.is_valid():
            pasajero = serializer.save()
            return success_response(
                PasajeroSerializer(pasajero).data,
                "Pasajero registrado exitosamente",
                status_code=status.HTTP_201_CREATED
            )
        return error_response("Datos inválidos", serializer.errors)
    
    def update(self, request, pk=None):
        """Actualizar un pasajero"""
        try:
            pasajero = PasajeroService.get_pasajero(pk)
            self.check_object_permissions(request, pasajero)
            
            serializer = PasajeroSerializer(data=request.data, partial=True)
            if serializer.is_valid():
                pasajero = PasajeroService.update_pasajero(pk, serializer.validated_data)
                return success_response(
                    PasajeroSerializer(pasajero).data,
                    "Pasajero actualizado exitosamente"
                )
            return error_response("Datos inválidos", serializer.errors)
        except Exception as e:
            return error_response(str(e), status_code=status.HTTP_404_NOT_FOUND)
    
    @swagger_auto_schema(
        operation_description="Obtener todas las reservas de un pasajero",
        responses={200: ReservaDetailSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def reservas(self, request, pk=None):
        """Obtener todas las reservas de un pasajero"""
        try:
            pasajero = PasajeroService.get_pasajero(pk)
            self.check_object_permissions(request, pasajero)
            
            reservas = PasajeroService.get_reservas_pasajero(pk)
            serializer = ReservaDetailSerializer(reservas, many=True)
            return success_response(serializer.data, "Reservas obtenidas exitosamente")
        except Exception as e:
            return error_response(str(e), status_code=status.HTTP_404_NOT_FOUND)
    
    @swagger_auto_schema(
        operation_description="Obtener reservas activas de un pasajero",
        responses={200: ReservaDetailSerializer(many=True)}
    )
    @action(detail=True, methods=['get'], url_path='reservas-activas')
    def reservas_activas(self, request, pk=None):
        """Obtener reservas activas de un pasajero"""
        try:
            pasajero = PasajeroService.get_pasajero(pk)
            self.check_object_permissions(request, pasajero)
            
            reservas = PasajeroService.get_reservas_activas_pasajero(pk)
            serializer = ReservaDetailSerializer(reservas, many=True)
            return success_response(serializer.data, "Reservas activas obtenidas exitosamente")
        except Exception as e:
            return error_response(str(e), status_code=status.HTTP_404_NOT_FOUND)
