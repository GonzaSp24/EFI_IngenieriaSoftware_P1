"""
Serializers para Pasajeros
"""
from rest_framework import serializers
from pasajeros.models import Pasajero
from django.contrib.auth.models import User


class PasajeroSerializer(serializers.ModelSerializer):
    """Serializer básico para Pasajero"""
    edad = serializers.SerializerMethodField()
    
    class Meta:
        model = Pasajero
        fields = [
            'id', 'nombre', 'apellido', 'tipo_documento', 'documento',
            'email', 'telefono', 'fecha_nacimiento', 'edad'
        ]
        read_only_fields = ['edad']
    
    def get_edad(self, obj):
        return obj.edad()


class PasajeroCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear un pasajero"""
    crear_usuario = serializers.BooleanField(default=False, write_only=True)
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Pasajero
        fields = [
            'nombre', 'apellido', 'tipo_documento', 'documento',
            'email', 'telefono', 'fecha_nacimiento', 'crear_usuario', 'password'
        ]
    
    def validate(self, data):
        """Validaciones personalizadas"""
        if data.get('crear_usuario') and not data.get('password'):
            raise serializers.ValidationError(
                "Debe proporcionar una contraseña si desea crear un usuario"
            )
        
        # Validar que el documento no exista
        if Pasajero.objects.filter(documento=data['documento']).exists():
            raise serializers.ValidationError(
                "Ya existe un pasajero con este documento"
            )
        
        # Validar que el email no exista
        if Pasajero.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError(
                "Ya existe un pasajero con este email"
            )
        
        return data
    
    def create(self, validated_data):
        """Crear pasajero y opcionalmente un usuario"""
        crear_usuario = validated_data.pop('crear_usuario', False)
        password = validated_data.pop('password', None)
        
        pasajero = Pasajero.objects.create(**validated_data)
        
        if crear_usuario and password:
            # Crear usuario asociado
            username = validated_data['email'].split('@')[0]
            user = User.objects.create_user(
                username=username,
                email=validated_data['email'],
                password=password,
                first_name=validated_data['nombre'],
                last_name=validated_data['apellido']
            )
            pasajero.usuario = user
            pasajero.save()
        
        return pasajero


class PasajeroDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para un pasajero con sus reservas"""
    edad = serializers.SerializerMethodField()
    total_reservas = serializers.SerializerMethodField()
    reservas_activas = serializers.SerializerMethodField()
    
    class Meta:
        model = Pasajero
        fields = [
            'id', 'nombre', 'apellido', 'tipo_documento', 'documento',
            'email', 'telefono', 'fecha_nacimiento', 'edad',
            'total_reservas', 'reservas_activas'
        ]
    
    def get_edad(self, obj):
        return obj.edad()
    
    def get_total_reservas(self, obj):
        return obj.reservas.count()
    
    def get_reservas_activas(self, obj):
        return obj.reservas.filter(estado='confirmada').count()
