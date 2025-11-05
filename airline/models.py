"""
Modelos de la aplicación Airline.
Contiene todos los modelos del sistema: Avion, Vuelo, Asiento, Pasajero, Reserva y Boleto.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from datetime import date
import uuid
import random
import string


class Avion(models.Model):
    """
    Modelo que representa un avión de la flota.
    Gestiona la información del avión y crea automáticamente sus asientos.
    """
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
                    estado='disponible'
                )


class Asiento(models.Model):
    """
    Modelo que representa un asiento dentro de un avión.
    Cada asiento tiene un número, tipo y estado.
    """
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


class Vuelo(models.Model):
    """
    Modelo que representa un vuelo programado.
    Contiene información sobre origen, destino, fechas y estado del vuelo.
    """
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
                'estado_vuelo': estado_vuelo,
                'pasajero': pasajero,
                'reserva': reserva_confirmada
            })
        
        return asientos_info


class Pasajero(models.Model):
    """
    Modelo que representa un pasajero del sistema.
    Puede estar vinculado a un usuario del sistema o ser independiente.
    """
    # Vinculación opcional con usuario del sistema
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='pasajero')
    
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
    fecha_nacimiento = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Pasajero"
        verbose_name_plural = "Pasajeros"
        ordering = ['apellido', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.documento})"
    
    def edad(self):
        if not self.fecha_nacimiento:
            return "N/A"
        today = date.today()
        return (today.year - self.fecha_nacimiento.year - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
    )


class Reserva(models.Model):
    """
    Modelo que representa una reserva de vuelo.
    Vincula un pasajero con un vuelo y un asiento específico.
    """
    vuelo = models.ForeignKey(Vuelo, on_delete=models.CASCADE, related_name='reservas')
    pasajero = models.ForeignKey(Pasajero, on_delete=models.CASCADE, related_name='reservas')
    asiento = models.ForeignKey(Asiento, on_delete=models.CASCADE, related_name='reservas')

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
            self.codigo_reserva = self._generar_codigo_reserva()
        super().save(*args, **kwargs)
        
        # Actualizar estado del asiento después de guardar la reserva
        if self.estado == 'confirmada':
            self.asiento.estado = 'ocupado'
            self.asiento.save()
        elif self.estado == 'cancelada':
            self.asiento.estado = 'disponible'
            self.asiento.save()

    def _generar_codigo_reserva(self):
        """Genera un código único de reserva de 8 caracteres"""
        while True:
            codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not Reserva.objects.filter(codigo_reserva=codigo).exists():
                return codigo

    def __str__(self):
        return f"Reserva {self.codigo_reserva} - Vuelo {self.vuelo.origen}-{self.vuelo.destino} - Pasajero {self.pasajero.nombre} {self.pasajero.apellido}"


class Boleto(models.Model):
    """
    Modelo que representa un boleto electrónico.
    Se genera automáticamente cuando una reserva es confirmada.
    """
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
