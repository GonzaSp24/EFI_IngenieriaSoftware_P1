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
    
    def save(self, *args, **kwargs):
        # Calcular capacidad automáticamente
        self.capacidad = self.filas * self.columnas
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.crear_asientos()
    
    def crear_asientos(self):
        """Crear asientos automáticamente cuando se crea un avión"""
        for fila in range(1, self.filas + 1):
            for col_idx in range(self.columnas):
                columna_letra = chr(65 + col_idx)  # A, B, C, D, E, F
                numero_asiento = f"{fila}{columna_letra}"
                
                # Determinar tipo de asiento según la fila
                if fila <= 3:
                    tipo = 'primera'
                elif fila <= 10:
                    tipo = 'ejecutivo'
                else:
                    tipo = 'economico'
                
                Asiento.objects.create(
                    avion=self,
                    numero=numero_asiento,
                    fila=fila,
                    columna=columna_letra,
                    tipo=tipo,
                    estado='disponible'  # IMPORTANTE: Crear como disponible
                )

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
        """Retorna el número de asientos disponibles para este vuelo"""
        total_asientos = self.avion.capacidad
        reservados = self.reservas.filter(estado='confirmada').count()
        return total_asientos - reservados
    
    def get_asientos_con_estado_para_vuelo(self):
        """Retorna todos los asientos del avión con su estado para este vuelo"""
        asientos_info = []
        
        for asiento in self.avion.asiento_set.all().order_by('fila', 'columna'):
            # Verificar si hay una reserva confirmada para este asiento en este vuelo
            reserva_confirmada = self.reservas.filter(
                asiento=asiento, 
                estado='confirmada'
            ).first()
            
            if reserva_confirmada:
                estado_vuelo = 'ocupado'
                pasajero = reserva_confirmada.pasajero
            else:
                estado_vuelo = 'disponible'
                pasajero = None
            
            asientos_info.append({
                'asiento': asiento,
                'estado_vuelo': estado_vuelo,  # Este es el estado para este vuelo específico
                'pasajero': pasajero,
                'reserva': reserva_confirmada
            })
        
        return asientos_info

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
