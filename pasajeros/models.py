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

    class Meta:
        verbose_name = "Pasajero"
        verbose_name_plural = "Pasajeros"
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.documento})"

    def edad(self):
        from datetime import date
        today = date.today()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )
