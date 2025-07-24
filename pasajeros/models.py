from django.db import models

# Create your models here.
# pasajeros/models.py
from django.db import models

class Pasajero(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    tipo_documento_choices = [
        ('DNI', 'DNI'),
        ('PAS', 'Pasaporte'),
        ('LC', 'Libreta Cívica'),
        ('LE', 'Libreta de Enrolamiento'),
    ]
    tipo_documento = models.CharField(max_length=10, choices=tipo_documento_choices)
    documento = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_nacimiento = models.DateField()

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.documento})"
