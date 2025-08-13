from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
    Modelo de usuario personalizado que extiende AbstractUser
    """
    rol_choices = [
        ('admin', 'Administrador'),
        ('empleado', 'Empleado'),
        ('cliente', 'Cliente'),
    ]
    rol = models.CharField(max_length=20, choices=rol_choices, default='cliente')
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    
    class Meta:
        app_label = 'usuarios'  # ✅ AGREGADO - Especifica la app
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"
    
    @property
    def is_admin(self):
        return self.rol == 'admin' or self.is_staff or self.is_superuser
    
    @property
    def is_empleado(self):
        return self.rol == 'empleado' or self.is_staff
