from django.db import models
from django.contrib.auth.models import User

class CategoriaLicencia(models.Model):
    codigo = models.CharField(max_length=1, unique=True)
    descripcion = models.CharField(max_length=100)

    def __str__(self):
        return self.codigo

class SubcategoriaLicencia(models.Model):
    codigo = models.CharField(max_length=3, unique=True)
    descripcion = models.TextField()
    categoria = models.ForeignKey(CategoriaLicencia, on_delete=models.CASCADE, related_name='subcategorias')

    def __str__(self):
        return self.codigo

class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cliente')
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    licencia = models.ForeignKey(SubcategoriaLicencia, on_delete=models.CASCADE, related_name='clientes')
    telefono = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Vehiculo(models.Model):
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    placa = models.CharField(max_length=20, unique=True)
    costo_dia = models.DecimalField(max_digits=10, decimal_places=2)
    color = models.CharField(max_length=30, blank=True, null=True)
    disponible = models.BooleanField(default=True)
    imagen = models.ImageField(upload_to='vehiculos/', blank=True, null=True, help_text='Imagen del vehículo')

    def __str__(self):
        return f"{self.marca} {self.modelo} - {self.placa}"

class Reserva(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
    ]

    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name='reservas')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='reservas')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=15, choices=ESTADOS, default='pendiente')

    def __str__(self):
        return f"Reserva {self.pk} - {self.cliente}"
    
    def calcular_total(self):
        """Calcula el total basado en días de alquiler"""
        if self.fecha_inicio and self.fecha_fin and self.vehiculo:
            dias = (self.fecha_fin - self.fecha_inicio).days + 1
            return self.vehiculo.costo_dia * dias
        return self.total
    
    def crear_factura_automatica(self):
        """Crea una factura automáticamente al confirmar la reserva"""
        from django.utils import timezone
        from uuid import uuid4
        
        # Verificar si ya existe factura
        if hasattr(self, 'factura'):
            return self.factura
        
        # Generar número único de factura
        numero_factura = f"FCT-{self.pk}-{uuid4().hex[:8].upper()}"
        
        # Crear factura
        factura = Factura.objects.create(
            reserva=self,
            numero=numero_factura,
            monto=self.total,
            fecha_emision=timezone.now().date()
        )
        return factura

class Devolucion(models.Model):
    ESTADOS_DEVOLUCION = [
        ('entregado', 'Entregado'),
        ('atrasado', 'Atrasado'),
        ('danado', 'Dañado'),
    ]

    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE, related_name='devolucion')
    fecha_devolucion = models.DateField()
    estado_devolucion = models.CharField(max_length=20, choices=ESTADOS_DEVOLUCION)
    penalizacion = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Devolución {self.pk} - Reserva {self.reserva.pk}"
    
    def calcular_penalizacion(self):
        """Calcula la penalización basada en el estado de la devolución"""
        from decimal import Decimal
        from datetime import timedelta
        
        penalizacion = Decimal('0')
        
        # Penalización por atraso
        if self.estado_devolucion == 'atrasado':
            dias_atraso = (self.fecha_devolucion - self.reserva.fecha_fin).days
            if dias_atraso > 0:
                # Cobrar un 50% del costo diario por cada día de atraso
                penalizacion = dias_atraso * (self.reserva.vehiculo.costo_dia * Decimal('0.5'))
        
        # Penalización por daño
        elif self.estado_devolucion == 'danado':
            # Cobrar un 20% del valor total de la reserva
            penalizacion = self.reserva.total * Decimal('0.20')
        
        self.penalizacion = penalizacion
        return penalizacion
    
    def actualizar_factura_con_penalizacion(self):
        """Actualiza la factura con la penalización"""
        from decimal import Decimal
        
        if hasattr(self.reserva, 'factura'):
            factura = self.reserva.factura
            factura.monto = self.reserva.total + Decimal(str(self.penalizacion))
            factura.save()
            return factura
        return None

class Factura(models.Model):
    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE, related_name='factura')
    numero = models.CharField(max_length=30, unique=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_emision = models.DateField()

    def __str__(self):
        return self.numero
