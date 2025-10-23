"""
Views para reportes
"""
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from api.serializers import PasajeroSerializer, ReservaDetailSerializer
from api.services import VueloService, PasajeroService
from api.permissions import IsAdminUser
from api.utils import success_response, error_response
from api.repositories import ReservaRepository


class PasajerosPorVueloView(APIView):
    """
    Vista para obtener reporte de pasajeros por vuelo
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    @swagger_auto_schema(
        operation_description="Obtener lista de pasajeros de un vuelo específico",
        responses={200: PasajeroSerializer(many=True)}
    )
    def get(self, request, vuelo_id):
        """Obtener pasajeros de un vuelo"""
        try:
            vuelo = VueloService.get_vuelo(vuelo_id)
            reservas = ReservaRepository.get_by_vuelo(vuelo_id).filter(estado='confirmada')
            
            pasajeros = [reserva.pasajero for reserva in reservas]
            serializer = PasajeroSerializer(pasajeros, many=True)
            
            return success_response(
                {
                    'vuelo': f"{vuelo.origen} → {vuelo.destino}",
                    'fecha': vuelo.fecha_salida,
                    'total_pasajeros': len(pasajeros),
                    'pasajeros': serializer.data
                },
                "Reporte generado exitosamente"
            )
        except Exception as e:
            return error_response(str(e))


class ReservasActivasPasajeroView(APIView):
    """
    Vista para obtener reporte de reservas activas de un pasajero
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtener reservas activas de un pasajero",
        responses={200: ReservaDetailSerializer(many=True)}
    )
    def get(self, request, pasajero_id):
        """Obtener reservas activas de un pasajero"""
        try:
            # Verificar permisos
            if not request.user.is_staff:
                if not hasattr(request.user, 'pasajero') or request.user.pasajero.id != int(pasajero_id):
                    return error_response("No tiene permisos para ver este reporte", status_code=403)
            
            pasajero = PasajeroService.get_pasajero(pasajero_id)
            reservas = PasajeroService.get_reservas_activas_pasajero(pasajero_id)
            
            serializer = ReservaDetailSerializer(reservas, many=True)
            
            return success_response(
                {
                    'pasajero': f"{pasajero.nombre} {pasajero.apellido}",
                    'total_reservas_activas': len(reservas),
                    'reservas': serializer.data
                },
                "Reporte generado exitosamente"
            )
        except Exception as e:
            return error_response(str(e))
