from django.db import models

# Create your models here.
# reservas/models.py
from django.db import models
from vuelos.models import Vuelo, Asiento
from pasajeros.models import Pasajero
import uuid

class Reserva(models.Model):
    vuelo = models.ForeignKey(Vuelo, on_delete=models.CASCADE)
    pasajero = models.ForeignKey(Pasajero, on_delete=models.CASCADE)
    asiento = models.OneToOneField(Asiento, on_delete=models.PROTECT, null=True, blank=True)
    estado_choices = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
    ]
    estado = models.CharField(max_length=20, choices=estado_choices, default='pendiente')
    fecha_reserva = models.DateTimeField(auto_now_add=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    codigo_reserva = models.CharField(max_length=8, unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.codigo_reserva:
            self.codigo_reserva = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('vuelo', 'pasajero')

    def __str__(self):
        return f"Reserva {self.codigo_reserva} - Vuelo {self.vuelo} - Pasajero {self.pasajero}"

class Boleto(models.Model):
    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE)
    codigo_barra = models.CharField(max_length=50, unique=True, editable=False)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    estado_choices = [
        ('emitido', 'Emitido'),
        ('usado', 'Usado'),
        ('anulado', 'Anulado'),
    ]
    estado = models.CharField(max_length=20, choices=estado_choices, default='emitido')

    def save(self, *args, **kwargs):
        if not self.codigo_barra:
            self.codigo_barra = str(uuid.uuid4())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Boleto para reserva {self.reserva.codigo_reserva}"
