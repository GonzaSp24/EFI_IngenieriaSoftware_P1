"""
Views para Reservas y Boletos
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.serializers import (
    ReservaSerializer, ReservaCreateSerializer, ReservaDetailSerializer,
    BoletoSerializer, BoletoGenerateSerializer
)
from api.services import ReservaService, BoletoService
from api.permissions import IsAdminUser, IsOwnerOrAdmin
from api.utils import success_response, error_response


class ReservaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Reservas
    
    list: Listar reservas (admin: todas, usuario: propias)
    retrieve: Obtener detalle de una reserva
    create: Crear una nueva reserva
    confirmar: Confirmar una reserva
    cancelar: Cancelar una reserva
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Serializer según la acción"""
        if self.action == 'create':
            return ReservaCreateSerializer
        elif self.action in ['retrieve', 'list']:
            return ReservaDetailSerializer
        return ReservaSerializer
    
    def get_queryset(self):
        """Filtrar reservas según el usuario"""
        user = self.request.user
        if user.is_staff:
            return ReservaService.get_all_reservas()
        
        # Usuario normal solo ve sus propias reservas
        if hasattr(user, 'pasajero'):
            from api.repositories import PasajeroRepository
            return PasajeroRepository.get_reservas(user.pasajero.id)
        return []
    
    def list(self, request):
        """Listar reservas"""
        reservas = self.get_queryset()
        serializer = self.get_serializer_class()(reservas, many=True)
        return success_response(serializer.data, "Reservas obtenidas exitosamente")
    
    def retrieve(self, request, pk=None):
        """Obtener detalle de una reserva"""
        try:
            reserva = ReservaService.get_reserva(pk)
            self.check_object_permissions(request, reserva)
            serializer = self.get_serializer_class()(reserva)
            return success_response(serializer.data, "Reserva obtenida exitosamente")
        except Exception as e:
            return error_response(str(e), status_code=status.HTTP_404_NOT_FOUND)
    
    def create(self, request):
        """Crear una nueva reserva"""
        serializer = self.get_serializer_class()(data=request.data)
        if serializer.is_valid():
            try:
                reserva = ReservaService.create_reserva(serializer.validated_data)
                return success_response(
                    ReservaDetailSerializer(reserva).data,
                    "Reserva creada exitosamente",
                    status_code=status.HTTP_201_CREATED
                )
            except Exception as e:
                return error_response(str(e))
        return error_response("Datos inválidos", serializer.errors)
    
    @swagger_auto_schema(
        operation_description="Confirmar una reserva",
        responses={200: ReservaDetailSerializer()}
    )
    @action(detail=True, methods=['patch'], url_path='confirmar')
    def confirmar(self, request, pk=None):
        """Confirmar una reserva"""
        try:
            reserva = ReservaService.get_reserva(pk)
            self.check_object_permissions(request, reserva)
            
            reserva = ReservaService.confirmar_reserva(pk)
            return success_response(
                ReservaDetailSerializer(reserva).data,
                "Reserva confirmada exitosamente"
            )
        except Exception as e:
            return error_response(str(e))
    
    @swagger_auto_schema(
        operation_description="Cancelar una reserva",
        responses={200: ReservaDetailSerializer()}
    )
    @action(detail=True, methods=['patch'], url_path='cancelar')
    def cancelar(self, request, pk=None):
        """Cancelar una reserva"""
        try:
            reserva = ReservaService.get_reserva(pk)
            self.check_object_permissions(request, reserva)
            
            reserva = ReservaService.cancelar_reserva(pk)
            return success_response(
                ReservaDetailSerializer(reserva).data,
                "Reserva cancelada exitosamente"
            )
        except Exception as e:
            return error_response(str(e))


class BoletoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para gestión de Boletos
    
    list: Listar boletos (admin: todos, usuario: propios)
    retrieve: Obtener detalle de un boleto
    generar: Generar un boleto para una reserva
    consultar_codigo: Consultar un boleto por código de barra
    """
    serializer_class = BoletoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtrar boletos según el usuario"""
        user = self.request.user
        if user.is_staff:
            return BoletoService.get_all_boletos()
        
        # Usuario normal solo ve sus propios boletos
        if hasattr(user, 'pasajero'):
            from api.repositories import PasajeroRepository
            reservas = PasajeroRepository.get_reservas(user.pasajero.id)
            return [r.boleto for r in reservas if hasattr(r, 'boleto')]
        return []
    
    def list(self, request):
        """Listar boletos"""
        boletos = self.get_queryset()
        serializer = self.serializer_class(boletos, many=True)
        return success_response(serializer.data, "Boletos obtenidos exitosamente")
    
    def retrieve(self, request, pk=None):
        """Obtener detalle de un boleto"""
        try:
            boleto = BoletoService.get_boleto(pk)
            self.check_object_permissions(request, boleto)
            serializer = self.serializer_class(boleto)
            return success_response(serializer.data, "Boleto obtenido exitosamente")
        except Exception as e:
            return error_response(str(e), status_code=status.HTTP_404_NOT_FOUND)
    
    @swagger_auto_schema(
        operation_description="Generar un boleto para una reserva",
        request_body=BoletoGenerateSerializer,
        responses={201: BoletoSerializer()}
    )
    @action(detail=False, methods=['post'], url_path='generar')
    def generar(self, request):
        """Generar un boleto para una reserva"""
        serializer = BoletoGenerateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                reserva_id = serializer.validated_data['reserva_id']
                boleto = BoletoService.generar_boleto(reserva_id)
                return success_response(
                    BoletoSerializer(boleto).data,
                    "Boleto generado exitosamente",
                    status_code=status.HTTP_201_CREATED
                )
            except Exception as e:
                return error_response(str(e))
        return error_response("Datos inválidos", serializer.errors)
    
    @swagger_auto_schema(
        operation_description="Consultar un boleto por código de barra",
        manual_parameters=[
            openapi.Parameter('codigo', openapi.IN_PATH, description="Código de barra del boleto", type=openapi.TYPE_STRING),
        ],
        responses={200: BoletoSerializer()}
    )
    @action(detail=False, methods=['get'], url_path='consultar/(?P<codigo>[^/.]+)')
    def consultar_codigo(self, request, codigo=None):
        """Consultar un boleto por código de barra"""
        try:
            boleto = BoletoService.get_boleto_by_codigo(codigo)
            serializer = self.serializer_class(boleto)
            return success_response(serializer.data, "Boleto encontrado exitosamente")
        except Exception as e:
            return error_response(str(e), status_code=status.HTTP_404_NOT_FOUND)
