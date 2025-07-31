from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    rol_choices = [
        ('admin', 'Administrador'),
        ('empleado', 'Empleado'),
        ('cliente', 'Cliente'),
    ]
    rol = models.CharField(max_length=20, choices=rol_choices, default='cliente')
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return self.username
