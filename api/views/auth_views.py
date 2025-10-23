"""
Views para autenticación
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.serializers import PasajeroCreateSerializer
from api.utils import success_response, error_response


class RegisterView(APIView):
    """
    Vista para registro de usuarios
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Registrar un nuevo usuario y pasajero",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['nombre', 'apellido', 'documento', 'email', 'password', 'tipo_documento', 'fecha_nacimiento'],
            properties={
                'nombre': openapi.Schema(type=openapi.TYPE_STRING),
                'apellido': openapi.Schema(type=openapi.TYPE_STRING),
                'tipo_documento': openapi.Schema(type=openapi.TYPE_STRING),
                'documento': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'telefono': openapi.Schema(type=openapi.TYPE_STRING),
                'fecha_nacimiento': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={201: 'Usuario registrado exitosamente'}
    )
    def post(self, request):
        """Registrar un nuevo usuario"""
        data = request.data.copy()
        data['crear_usuario'] = True
        
        serializer = PasajeroCreateSerializer(data=data)
        if serializer.is_valid():
            pasajero = serializer.save()
            
            # Generar tokens JWT
            refresh = RefreshToken.for_user(pasajero.usuario)
            
            return success_response(
                {
                    'user': {
                        'id': pasajero.usuario.id,
                        'username': pasajero.usuario.username,
                        'email': pasajero.usuario.email,
                        'pasajero_id': pasajero.id
                    },
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                },
                "Usuario registrado exitosamente",
                status_code=status.HTTP_201_CREATED
            )
        return error_response("Datos inválidos", serializer.errors)


class LoginView(APIView):
    """
    Vista para login de usuarios
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Iniciar sesión",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username o email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={200: 'Login exitoso'}
    )
    def post(self, request):
        """Iniciar sesión"""
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return error_response("Debe proporcionar username y password")
        
        # Intentar autenticar
        user = authenticate(username=username, password=password)
        
        # Si no funciona con username, intentar con email
        if not user:
            try:
                user_obj = User.objects.get(email=username)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        if user:
            # Generar tokens JWT
            refresh = RefreshToken.for_user(user)
            
            # Obtener información del pasajero si existe
            pasajero_id = None
            if hasattr(user, 'pasajero'):
                pasajero_id = user.pasajero.id
            
            return success_response(
                {
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'is_staff': user.is_staff,
                        'pasajero_id': pasajero_id
                    },
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                },
                "Login exitoso"
            )
        
        return error_response(
            "Credenciales inválidas",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
