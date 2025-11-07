"""
Serializers de la API REST
Todos los serializers en un solo archivo siguiendo el patrón de Mile
"""

from rest_framework import serializers
from airline.models import Vuelo, Avion, Asiento, Pasajero, Reserva, Boleto
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed

from airline.services import (
    VueloService,
    AvionService,
    PasajeroService,
    ReservaService,
    BoletoService,
)

class AsientoMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asiento
        fields = ["id", "fila", "columna", "numero", "tipo"]

class PasajeroMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pasajero
        fields = ["id", "nombre", "apellido", "documento"]

class ReservaMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reserva
        fields = ["id", "estado", "codigo_reserva"]

# ============================================================================
# SERIALIZERS DE LOGIN Y REGISTRO
# ============================================================================

class LoginSerializer(serializers.Serializer):
    """
    Serializer para manejar la autenticación de usuarios (login).
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        user = authenticate(username=username, password=password)
        if not user:
            raise AuthenticationFailed("Credenciales inválidas.")

        attrs["user"] = user
        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer para registrar nuevos usuarios.
    """
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "first_name", "last_name"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        return user


# ============================================================================
# SERIALIZERS DE AVIONES Y ASIENTOS
# ============================================================================


class AvionSerializer(serializers.ModelSerializer):
    """
    Serializer del modelo Avion.
    Usa ModelSerializer para mantener compatibilidad con la UI de DRF,
    pero delega la lógica de negocio al AvionService.
    """

    class Meta:
        model = Avion
        fields = ["id", "modelo", "capacidad", "filas", "columnas"]

    def create(self, validated_data):
        # le pasamos el dict tal cual
        return AvionService.create_avion(validated_data)
    
    def update(self, instance, validated_data):
        return AvionService.update_avion(instance.id, validated_data)


class AsientoSerializer(serializers.ModelSerializer):
    """
    Serializer del modelo Asiento.
    Delega la lógica de negocio a la capa de servicio.
    """

    # Para POST/PUT -> se pasa solo el id del avión
    avion = serializers.PrimaryKeyRelatedField(
        queryset=Avion.objects.all(), write_only=True
    )

    # Para GET -> se muestra el avión relacionado
    avion_display = serializers.StringRelatedField(source="avion", read_only=True)

    class Meta:
        model = Asiento
        fields = [
            "id",
            "numero",
            "fila",
            "columna",
            "tipo",
            "estado",
            "avion",
            "avion_display",
        ]


# ============================================================================
# SERIALIZERS DE VUELOS
# ============================================================================


class VueloListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar vuelos.
    Muestra solo información básica para optimizar las consultas.
    """

    avion_modelo = serializers.CharField(source="avion.modelo", read_only=True)

    class Meta:
        model = Vuelo
        fields = [
            "id",
            "origen",
            "destino",
            "fecha_salida",
            "fecha_llegada",
            "precio_base",
            "estado",
            "avion_modelo",
        ]


class VueloDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detallado para un vuelo específico.
    Incluye información completa del avión y asientos disponibles.
    """

    avion = AvionSerializer(read_only=True)
    asientos_disponibles = serializers.SerializerMethodField()
    asientos = serializers.SerializerMethodField() 
    class Meta:
        model = Vuelo
        fields = [
            "id",
            "origen",
            "destino",
            "fecha_salida",
            "fecha_llegada",
            "duracion",
            "precio_base",
            "estado",
            "avion",
            "asientos_disponibles",
            "asientos",        
        ]

    def get_asientos_disponibles(self, obj):
        return VueloService.get_asientos_disponibles(obj.id)

    def get_asientos(self, obj):
        """
        Serializa la salida de obj.get_asientos_con_estado_para_vuelo(), que
        trae una lista de diccionarios con llaves: asiento, estado_vuelo, pasajero, reserva
        """
        items = []
        for info in obj.get_asientos_con_estado_para_vuelo():
            asiento = info.get("asiento")
            pasajero = info.get("pasajero")
            reserva = info.get("reserva")
            items.append({
                "asiento": AsientoMiniSerializer(asiento).data if asiento else None,
                "estado_vuelo": info.get("estado_vuelo"),
                "pasajero": PasajeroMiniSerializer(pasajero).data if pasajero else None,
                "reserva": ReservaMiniSerializer(reserva).data if reserva else None,
            })
        return items


class VueloSerializer(serializers.ModelSerializer):
    """
    Serializer completo para CRUD de vuelos.
    Usa ModelSerializer para compatibilidad con DRF,
    pero delega toda la lógica al VueloService.
    """

    # Para POST/PUT -> se pasa solo el id del avión
    avion = serializers.PrimaryKeyRelatedField(
        queryset=Avion.objects.all(), write_only=True
    )

    # Para GET -> se muestra el avión completo
    avion_display = AvionSerializer(source="avion", read_only=True)

    class Meta:
        model = Vuelo
        fields = [
            "id",
            "origen",
            "destino",
            "fecha_salida",
            "fecha_llegada",
            "duracion",
            "precio_base",
            "estado",
            "avion",
            "avion_display",
        ]
        read_only_fields = ["duracion"]

    def create(self, validated_data):
        """Crea un nuevo vuelo usando la capa de servicio"""
        return VueloService.create_vuelo(
            origen=validated_data["origen"],
            destino=validated_data["destino"],
            fecha_salida=validated_data["fecha_salida"],
            fecha_llegada=validated_data["fecha_llegada"],
            precio_base=validated_data["precio_base"],
            estado=validated_data["estado"],
            avion_id=validated_data["avion"].id,
        )

    def update(self, instance, validated_data):
        """Actualiza un vuelo existente usando la capa de servicio"""
        return VueloService.update_vuelo(
            vuelo_id=instance.id,
            origen=validated_data.get("origen", instance.origen),
            destino=validated_data.get("destino", instance.destino),
            fecha_salida=validated_data.get("fecha_salida", instance.fecha_salida),
            fecha_llegada=validated_data.get("fecha_llegada", instance.fecha_llegada),
            precio_base=validated_data.get("precio_base", instance.precio_base),
            estado=validated_data.get("estado", instance.estado),
            avion_id=validated_data.get("avion", instance.avion).id,
        )


# ============================================================================
# SERIALIZERS DE PASAJEROS
# ============================================================================


class PasajeroSerializer(serializers.ModelSerializer):
    """
    Serializer del modelo Pasajero.
    Delega toda la lógica de creación y actualización al PasajeroService.
    """

    class Meta:
        model = Pasajero
        fields = [
            "id",
            "nombre",
            "apellido",
            "documento",
            "tipo_documento",
            "email",
            "telefono",
            "fecha_nacimiento",
        ]

    def create(self, validated_data):
        """Crea un nuevo pasajero usando la capa de servicio"""
        return PasajeroService.create_pasajero(
            nombre=validated_data["nombre"],
            apellido=validated_data["apellido"],
            documento=validated_data["documento"],
            tipo_documento=validated_data["tipo_documento"],
            email=validated_data["email"],
            telefono=validated_data.get("telefono", ""),
            fecha_nacimiento=validated_data["fecha_nacimiento"],
        )

    def update(self, instance, validated_data):
        """Actualiza un pasajero existente usando la capa de servicio"""
        return PasajeroService.update_pasajero(
            pasajero_id=instance.id,
            nombre=validated_data.get("nombre", instance.nombre),
            apellido=validated_data.get("apellido", instance.apellido),
            documento=validated_data.get("documento", instance.documento),
            tipo_documento=validated_data.get("tipo_documento", instance.tipo_documento),
            email=validated_data.get("email", instance.email),
            telefono=validated_data.get("telefono", instance.telefono),
            fecha_nacimiento=validated_data.get("fecha_nacimiento", instance.fecha_nacimiento),
        )



# ============================================================================
# SERIALIZERS DE RESERVAS
# ============================================================================


class ReservaSerializer(serializers.ModelSerializer):
    """
    Serializer del modelo Reserva.
    Delega la creación y actualización al ReservaService.
    """

    # Para POST/PUT -> se envía solo el id de las relaciones
    vuelo = serializers.PrimaryKeyRelatedField(
        queryset=Vuelo.objects.all(), write_only=True
    )
    pasajero = serializers.PrimaryKeyRelatedField(
        queryset=Pasajero.objects.all(), write_only=True
    )
    asiento = serializers.PrimaryKeyRelatedField(
        queryset=Asiento.objects.all(), write_only=True
    )
    usuario = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True
    )

    # Para GET -> se muestra la información completa
    vuelo_display = serializers.StringRelatedField(source="vuelo", read_only=True)
    pasajero_display = serializers.StringRelatedField(source="pasajero", read_only=True)
    asiento_display = serializers.StringRelatedField(source="asiento", read_only=True)
    usuario_display = serializers.StringRelatedField(source="usuario", read_only=True)

    class Meta:
        model = Reserva
        fields = [
            "id",
            "estado",
            "fecha_reserva",
            "precio",
            "codigo_reserva",
            "vuelo",
            "vuelo_display",
            "pasajero",
            "pasajero_display",
            "asiento",
            "asiento_display",
            "usuario",
            "usuario_display",
        ]

    def create(self, validated_data):
        """Crea una nueva reserva usando la capa de servicio"""
        # usuario desde el request (no del payload)
        user = None
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            user = request.user

        return ReservaService.create_reserva(
            vuelo_id=validated_data["vuelo"].id,
            pasajero_id=validated_data["pasajero"].id,
            asiento_id=validated_data["asiento"].id,
            usuario_id=(user.id if user else None),
            precio=validated_data.get("precio"),
            # si querés permitir código custom, pasalo; si no, que lo genere el service
            codigo_reserva=validated_data.get("codigo_reserva"),
            estado=validated_data.get("estado", "pendiente"),
        )

    def update(self, instance, validated_data):
        """Actualiza una reserva existente usando la capa de servicio"""
        return ReservaService.update_reserva(  # <— usa el mismo nombre siempre
            reserva_id=instance.id,
            estado=validated_data.get("estado", instance.estado),
            precio=validated_data.get("precio", instance.precio),
            vuelo_id=(validated_data.get("vuelo", instance.vuelo).id),
            pasajero_id=(validated_data.get("pasajero", instance.pasajero).id),
            asiento_id=(validated_data.get("asiento", instance.asiento).id),
        )


# ============================================================================
# SERIALIZERS DE BOLETOS
# ============================================================================


class BoletoSerializer(serializers.ModelSerializer):
    """
    Serializer del modelo Boleto.
    Delega toda la lógica de creación y actualización al BoletoService.
    """

    # Para POST/PUT -> solo se envía el id de la reserva
    reserva = serializers.PrimaryKeyRelatedField(
        queryset=Reserva.objects.all(), write_only=True
    )

    # Para GET -> se muestra la información expandida
    reserva_display = serializers.StringRelatedField(source="reserva", read_only=True)

    class Meta:
        model = Boleto
        fields = [
            "id",
            "codigo_barra",
            "fecha_emision",
            "estado",
            "reserva",
            "reserva_display",
        ]

    def create(self, validated_data):
        """Crea un nuevo boleto usando la capa de servicio"""
        return BoletoService.crear_boleto(
            reserva_id=validated_data["reserva"].id,
            codigo_barra=validated_data.get("codigo_barra"),
        )

    def update(self, instance, validated_data):
        """Actualiza un boleto existente usando la capa de servicio"""
        return BoletoService.actualizar_boleto(
            boleto_id=instance.id,
            estado=validated_data.get("estado", instance.estado),
            codigo_barra=validated_data.get("codigo_barra", instance.codigo_barra),
        )
