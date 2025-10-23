"""
Views para Vuelos, Aviones y Asientos
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.serializers import (
    VueloSerializer, VueloListSerializer, VueloDetailSerializer,
    AvionSerializer, AsientoSerializer, AsientoDisponibilidadSerializer
)
from api.services import VueloService, AvionService, AsientoService
from api.permissions import IsAdminUser
from api.utils import success_response, error_response


class AvionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Aviones
    
    list: Listar todos los aviones
    retrieve: Obtener detalle de un avión
    create: Crear un nuevo avión (solo admin)
    update: Actualizar un avión (solo admin)
    destroy: Eliminar un avión (solo admin)
    asientos: Obtener asientos de un avión
    """
    serializer_class = AvionSerializer
    
    def get_permissions(self):
        """Permisos según la acción"""
        if self.action in ['list', 'retrieve', 'asientos']:
            return [AllowAny()]
        return [IsAdminUser()]
    
    def get_queryset(self):
        return AvionService.get_all_aviones()
    
    def list(self, request):
        """Listar todos los aviones"""
        aviones = self.get_queryset()
        serializer = self.serializer_class(aviones, many=True)
        return success_response(serializer.data, "Aviones obtenidos exitosamente")
    
    def retrieve(self, request, pk=None):
        """Obtener detalle de un avión"""
        try:
            avion = AvionService.get_avion(pk)
            serializer = self.serializer_class(avion)
            return success_response(serializer.data, "Avión obtenido exitosamente")
        except Exception as e:
            return error_response(str(e), status_code=status.HTTP_404_NOT_FOUND)
    
    def create(self, request):
        """Crear un nuevo avión"""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            avion = AvionService.create_avion(serializer.validated_data)
            return success_response(
                self.serializer_class(avion).data,
                "Avión creado exitosamente",
                status_code=status.HTTP_201_CREATED
            )
        return error_response("Datos inválidos", serializer.errors)
    
    @swagger_auto_schema(
        operation_description="Obtener todos los asientos de un avión",
        responses={200: AsientoSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def asientos(self, request, pk=None):
        """Obtener asientos de un avión"""
        try:
            asientos = AsientoService.get_asientos_by_avion(pk)
            serializer = AsientoSerializer(asientos, many=True)
            return success_response(serializer.data, "Asientos obtenidos exitosamente")
        except Exception as e:
            return error_response(str(e), status_code=status.HTTP_404_NOT_FOUND)


class VueloViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Vuelos
    
    list: Listar vuelos (con filtros opcionales)
    retrieve: Obtener detalle de un vuelo
    create: Crear un nuevo vuelo (solo admin)
    update: Actualizar un vuelo (solo admin)
    destroy: Eliminar un vuelo (solo admin)
    asientos_disponibles: Ver asientos disponibles para un vuelo
    """
    
    def get_permissions(self):
        """Permisos según la acción"""
        if self.action in ['list', 'retrieve', 'asientos_disponibles']:
            return [AllowAny()]
        return [IsAdminUser()]
    
    def get_serializer_class(self):
        """Serializer según la acción"""
        if self.action == 'list':
            return VueloListSerializer
        elif self.action == 'retrieve':
            return VueloDetailSerializer
        return VueloSerializer
    
    @swagger_auto_schema(
        operation_description="Listar vuelos con filtros opcionales",
        manual_parameters=[
            openapi.Parameter('origen', openapi.IN_QUERY, description="Filtrar por origen", type=openapi.TYPE_STRING),
            openapi.Parameter('destino', openapi.IN_QUERY, description="Filtrar por destino", type=openapi.TYPE_STRING),
            openapi.Parameter('fecha', openapi.IN_QUERY, description="Filtrar por fecha (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('estado', openapi.IN_QUERY, description="Filtrar por estado", type=openapi.TYPE_STRING),
        ]
    )
    def list(self, request):
        """Listar vuelos con filtros opcionales"""
        origen = request.query_params.get('origen')
        destino = request.query_params.get('destino')
        fecha = request.query_params.get('fecha')
        estado = request.query_params.get('estado')
        
        vuelos = VueloService.filter_vuelos(origen, destino, fecha, estado)
        serializer = self.get_serializer_class()(vuelos, many=True)
        return success_response(serializer.data, "Vuelos obtenidos exitosamente")
    
    def retrieve(self, request, pk=None):
        """Obtener detalle de un vuelo"""
        try:
            vuelo = VueloService.get_vuelo(pk)
            serializer = self.get_serializer_class()(vuelo)
            return success_response(serializer.data, "Vuelo obtenido exitosamente")
        except Exception as e:
            return error_response(str(e), status_code=status.HTTP_404_NOT_FOUND)
    
    def create(self, request):
        """Crear un nuevo vuelo"""
        serializer = self.get_serializer_class()(data=request.data)
        if serializer.is_valid():
            vuelo = VueloService.create_vuelo(serializer.validated_data)
            return success_response(
                VueloDetailSerializer(vuelo).data,
                "Vuelo creado exitosamente",
                status_code=status.HTTP_201_CREATED
            )
        return error_response("Datos inválidos", serializer.errors)
    
    def update(self, request, pk=None):
        """Actualizar un vuelo"""
        serializer = self.get_serializer_class()(data=request.data, partial=True)
        if serializer.is_valid():
            try:
                vuelo = VueloService.update_vuelo(pk, serializer.validated_data)
                return success_response(
                    VueloDetailSerializer(vuelo).data,
                    "Vuelo actualizado exitosamente"
                )
            except Exception as e:
                return error_response(str(e), status_code=status.HTTP_404_NOT_FOUND)
        return error_response("Datos inválidos", serializer.errors)
    
    def destroy(self, request, pk=None):
        """Eliminar un vuelo"""
        try:
            VueloService.delete_vuelo(pk)
            return success_response(None, "Vuelo eliminado exitosamente")
        except Exception as e:
            return error_response(str(e), status_code=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_description="Obtener asientos disponibles para un vuelo",
        responses={200: AsientoDisponibilidadSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def asientos_disponibles(self, request, pk=None):
        """Ver asientos disponibles para un vuelo"""
        try:
            asientos_info = VueloService.get_asientos_disponibles(pk)
            
            # Formatear la respuesta
            data = []
            for info in asientos_info:
                data.append({
                    'asiento_id': info['asiento'].id,
                    'numero': info['asiento'].numero,
                    'tipo': info['asiento'].tipo,
                    'disponible': info['estado_vuelo'] == 'disponible',
                    'pasajero': f"{info['pasajero'].nombre} {info['pasajero'].apellido}" if info['pasajero'] else None
                })
            
            return success_response(data, "Asientos obtenidos exitosamente")
        except Exception as e:
            return error_response(str(e), status_code=status.HTTP_404_NOT_FOUND)


class AsientoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para consulta de Asientos
    
    retrieve: Obtener detalle de un asiento
    disponibilidad: Verificar disponibilidad de un asiento para un vuelo
    """
    serializer_class = AsientoSerializer
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Verificar disponibilidad de un asiento para un vuelo",
        manual_parameters=[
            openapi.Parameter('vuelo_id', openapi.IN_QUERY, description="ID del vuelo", type=openapi.TYPE_INTEGER, required=True),
        ]
    )
    @action(detail=True, methods=['get'])
    def disponibilidad(self, request, pk=None):
        """Verificar disponibilidad de un asiento para un vuelo"""
        vuelo_id = request.query_params.get('vuelo_id')
        
        if not vuelo_id:
            return error_response("Debe proporcionar el ID del vuelo")
        
        try:
            disponible = AsientoService.check_disponibilidad(pk, vuelo_id)
            return success_response(
                {'disponible': disponible},
                "Disponibilidad verificada exitosamente"
            )
        except Exception as e:
            return error_response(str(e), status_code=status.HTTP_404_NOT_FOUND)
