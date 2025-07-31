from django.db import models
from django.core.validators import MinValueValidator

class Avion(models.Model):
    modelo = models.CharField(max_length=100)
    capacidad = models.IntegerField(validators=[MinValueValidator(1)])
    filas = models.IntegerField(validators=[MinValueValidator(1)])
    columnas = models.IntegerField(validators=[MinValueValidator(1)])
    
    class Meta:
        verbose_name = "Avión"
        verbose_name_plural = "Aviones"
    
    def __str__(self):
        return f"{self.modelo} ({self.capacidad} asientos)"
    
    def asientos_disponibles_count(self):
        """Retorna el número de asientos disponibles"""
        return self.asiento_set.filter(estado='disponible').count()

class Vuelo(models.Model):
    avion = models.ForeignKey(Avion, on_delete=models.PROTECT)
    origen = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)
    fecha_salida = models.DateTimeField()
    fecha_llegada = models.DateTimeField()
    duracion = models.DurationField()
    estado_choices = [
        ('programado', 'Programado'),
        ('en_curso', 'En Curso'),
        ('aterrizado', 'Aterrizado'),
        ('cancelado', 'Cancelado'),
        ('retrasado', 'Retrasado'),
    ]
    estado = models.CharField(max_length=20, choices=estado_choices, default='programado')
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = "Vuelo"
        verbose_name_plural = "Vuelos"
        ordering = ['fecha_salida']
    
    def __str__(self):
        return f"Vuelo de {self.origen} a {self.destino} ({self.fecha_salida.strftime('%Y-%m-%d %H:%M')})"
    
    def asientos_disponibles_count(self):
        total_asientos = self.avion.capacidad
        reservados = self.reservas.filter(estado='confirmada').count()
        return total_asientos - reservados


class Asiento(models.Model):
    avion = models.ForeignKey(Avion, on_delete=models.CASCADE)
    numero = models.CharField(max_length=10)
    fila = models.IntegerField()
    columna = models.CharField(max_length=2)
    tipo_choices = [
        ('economico', 'Económico'),
        ('ejecutivo', 'Ejecutivo'),
        ('primera', 'Primera Clase'),
    ]
    tipo = models.CharField(max_length=20, choices=tipo_choices, default='economico')
    estado_choices = [
        ('disponible', 'Disponible'),
        ('reservado', 'Reservado'),
        ('ocupado', 'Ocupado'),
        ('mantenimiento', 'Mantenimiento'),
    ]
    estado = models.CharField(max_length=20, choices=estado_choices, default='disponible')
    
    class Meta:
        verbose_name = "Asiento"
        verbose_name_plural = "Asientos"
        unique_together = ('avion', 'fila', 'columna')
        ordering = ['fila', 'columna']
    
    def __str__(self):
        return f"Avión: {self.avion.modelo}, Asiento: {self.numero} ({self.tipo})"
