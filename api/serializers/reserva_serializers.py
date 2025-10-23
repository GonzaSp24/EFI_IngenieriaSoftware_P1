"""
Serializers para Reservas y Boletos
"""
from rest_framework import serializers
from reservas.models import Reserva, Boleto
from .vuelo_serializers import VueloListSerializer, AsientoSerializer
from .pasajero_serializers import PasajeroSerializer


class ReservaSerializer(serializers.ModelSerializer):
    """Serializer básico para Reserva"""
    vuelo_info = serializers.SerializerMethodField()
    pasajero_info = serializers.SerializerMethodField()
    asiento_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Reserva
        fields = [
            'id', 'vuelo', 'pasajero', 'asiento', 'estado',
            'fecha_reserva', 'precio', 'codigo_reserva',
            'vuelo_info', 'pasajero_info', 'asiento_info'
        ]
        read_only_fields = ['codigo_reserva', 'fecha_reserva']
    
    def get_vuelo_info(self, obj):
        return f"{obj.vuelo.origen} → {obj.vuelo.destino}"
    
    def get_pasajero_info(self, obj):
        return f"{obj.pasajero.nombre} {obj.pasajero.apellido}"
    
    def get_asiento_info(self, obj):
        return obj.asiento.numero


class ReservaCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear una reserva"""
    
    class Meta:
        model = Reserva
        fields = ['vuelo', 'pasajero', 'asiento', 'precio']
    
    def validate(self, data):
        """Validaciones personalizadas"""
        vuelo = data.get('vuelo')
        pasajero = data.get('pasajero')
        asiento = data.get('asiento')
        
        # Validar que el asiento pertenezca al avión del vuelo
        if asiento.avion != vuelo.avion:
            raise serializers.ValidationError(
                "El asiento no pertenece al avión de este vuelo"
            )
        
        # Validar que el pasajero no tenga ya una reserva para este vuelo
        if Reserva.objects.filter(vuelo=vuelo, pasajero=pasajero).exclude(estado='cancelada').exists():
            raise serializers.ValidationError(
                "El pasajero ya tiene una reserva para este vuelo"
            )
        
        # Validar que el asiento esté disponible para este vuelo
        reserva_existente = Reserva.objects.filter(
            vuelo=vuelo,
            asiento=asiento,
            estado='confirmada'
        ).exists()
        
        if reserva_existente:
            raise serializers.ValidationError(
                "El asiento ya está reservado para este vuelo"
            )
        
        return data


class ReservaDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para una reserva"""
    vuelo = VueloListSerializer(read_only=True)
    pasajero = PasajeroSerializer(read_only=True)
    asiento = AsientoSerializer(read_only=True)
    tiene_boleto = serializers.SerializerMethodField()
    
    class Meta:
        model = Reserva
        fields = [
            'id', 'vuelo', 'pasajero', 'asiento', 'estado',
            'fecha_reserva', 'precio', 'codigo_reserva', 'tiene_boleto'
        ]
    
    def get_tiene_boleto(self, obj):
        return hasattr(obj, 'boleto')


class BoletoSerializer(serializers.ModelSerializer):
    """Serializer para Boleto"""
    reserva_detalle = ReservaDetailSerializer(source='reserva', read_only=True)
    
    class Meta:
        model = Boleto
        fields = [
            'id', 'reserva', 'codigo_barra', 'fecha_emision',
            'estado', 'reserva_detalle'
        ]
        read_only_fields = ['codigo_barra', 'fecha_emision']


class BoletoGenerateSerializer(serializers.Serializer):
    """Serializer para generar un boleto desde una reserva"""
    reserva_id = serializers.IntegerField()
    
    def validate_reserva_id(self, value):
        """Validar que la reserva exista y esté confirmada"""
        try:
            reserva = Reserva.objects.get(id=value)
        except Reserva.DoesNotExist:
            raise serializers.ValidationError("La reserva no existe")
        
        if reserva.estado != 'confirmada':
            raise serializers.ValidationError(
                "Solo se pueden generar boletos para reservas confirmadas"
            )
        
        if hasattr(reserva, 'boleto'):
            raise serializers.ValidationError(
                "Esta reserva ya tiene un boleto generado"
            )
        
        return value
