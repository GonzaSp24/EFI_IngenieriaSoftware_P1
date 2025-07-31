from django.db import models
from pasajeros.models import Pasajero
import uuid

class Reserva(models.Model):
    vuelo = models.ForeignKey('vuelos.Vuelo', on_delete=models.CASCADE, related_name='reservas')
    pasajero = models.ForeignKey(Pasajero, on_delete=models.CASCADE, related_name='reservas')
    asiento = models.ForeignKey('vuelos.Asiento', on_delete=models.CASCADE, related_name='reservas')

    estado_choices = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
    ]
    estado = models.CharField(max_length=20, choices=estado_choices, default='pendiente')
    fecha_reserva = models.DateTimeField(auto_now_add=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    codigo_reserva = models.CharField(max_length=8, unique=True, editable=False)

    class Meta:
        unique_together = ('vuelo', 'pasajero')
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ['-fecha_reserva']

    def save(self, *args, **kwargs):
        if not self.codigo_reserva:
            self.codigo_reserva = str(uuid.uuid4())[:8].upper()
        # Importación local para evitar circular import
        if self.estado == 'confirmada' and self.asiento.estado != 'ocupado':
            self.asiento.estado = 'ocupado'
            self.asiento.save()
        elif self.estado == 'cancelada' and self.asiento.estado != 'disponible':
            self.asiento.estado = 'disponible'
            self.asiento.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Reserva {self.codigo_reserva} - Vuelo {self.vuelo.origen}-{self.vuelo.destino} - Pasajero {self.pasajero.nombre} {self.pasajero.apellido}"

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

    class Meta:
        verbose_name = "Boleto"
        verbose_name_plural = "Boletos"
        ordering = ['-fecha_emision']

    def save(self, *args, **kwargs):
        if not self.codigo_barra:
            self.codigo_barra = str(uuid.uuid4())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Boleto para reserva {self.reserva.codigo_reserva}"
