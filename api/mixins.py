from rest_framework.permissions import IsAuthenticated, IsAdminUser


class AuthView:
    """
    Mixin para vistas que requieren autenticación.
    Hereda de esta clase para asegurar que solo usuarios autenticados puedan acceder.

    Uso:
        class MiVista(AuthView, ListAPIView):
            ...
    """

    permission_classes = [IsAuthenticated]


class AuthAdminView:
    """
    Mixin para vistas que requieren permisos de administrador.
    Hereda de esta clase para asegurar que solo administradores puedan acceder.

    Uso:
        class MiVistaAdmin(AuthAdminView, viewsets.ModelViewSet):
            ...
    """

    permission_classes = [IsAdminUser]
