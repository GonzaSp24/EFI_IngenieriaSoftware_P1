"""
Serializers para Vuelos, Aviones y Asientos
"""
from rest_framework import serializers
from vuelos.models import Vuelo, Avion, Asiento


class AvionSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Avion"""
    
    class Meta:
        model = Avion
        fields = ['id', 'modelo', 'capacidad', 'filas', 'columnas']
        read_only_fields = ['capacidad']


class AsientoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Asiento"""
    avion_modelo = serializers.CharField(source='avion.modelo', read_only=True)
    
    class Meta:
        model = Asiento
        fields = ['id', 'avion', 'avion_modelo', 'numero', 'fila', 'columna', 'tipo', 'estado']
        read_only_fields = ['numero']


class AsientoDisponibilidadSerializer(serializers.Serializer):
    """Serializer para verificar disponibilidad de asiento"""
    asiento_id = serializers.IntegerField()
    numero = serializers.CharField()
    tipo = serializers.CharField()
    disponible = serializers.BooleanField()
    pasajero = serializers.CharField(allow_null=True)


class VueloListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado de vuelos"""
    avion_modelo = serializers.CharField(source='avion.modelo', read_only=True)
    asientos_disponibles = serializers.SerializerMethodField()
    
    class Meta:
        model = Vuelo
        fields = [
            'id', 'origen', 'destino', 'fecha_salida', 'fecha_llegada',
            'duracion', 'estado', 'precio_base', 'avion_modelo', 'asientos_disponibles'
        ]
    
    def get_asientos_disponibles(self, obj):
        return obj.asientos_disponibles_count()


class VueloDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para un vuelo específico"""
    avion = AvionSerializer(read_only=True)
    asientos_disponibles = serializers.SerializerMethodField()
    total_reservas = serializers.SerializerMethodField()
    
    class Meta:
        model = Vuelo
        fields = [
            'id', 'avion', 'origen', 'destino', 'fecha_salida', 'fecha_llegada',
            'duracion', 'estado', 'precio_base', 'asientos_disponibles', 'total_reservas'
        ]
    
    def get_asientos_disponibles(self, obj):
        return obj.asientos_disponibles_count()
    
    def get_total_reservas(self, obj):
        return obj.reservas.filter(estado='confirmada').count()


class VueloSerializer(serializers.ModelSerializer):
    """Serializer completo para crear/editar vuelos"""
    
    class Meta:
        model = Vuelo
        fields = [
            'id', 'avion', 'origen', 'destino', 'fecha_salida', 'fecha_llegada',
            'duracion', 'estado', 'precio_base'
        ]
    
    def validate(self, data):
        """Validaciones personalizadas"""
        if data.get('fecha_salida') and data.get('fecha_llegada'):
            if data['fecha_llegada'] <= data['fecha_salida']:
                raise serializers.ValidationError(
                    "La fecha de llegada debe ser posterior a la fecha de salida"
                )
        
        if data.get('precio_base') and data['precio_base'] <= 0:
            raise serializers.ValidationError(
                "El precio base debe ser mayor a 0"
            )
        
        return data
