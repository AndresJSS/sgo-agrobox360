from django.db import models
from django.utils import timezone
from datetime import timedelta
from datetime import datetime
import uuid

class Cultivo(models.Model):
    OPCIONES_CULTIVO = [
        ('Lechuga', 'Lechuga'),
        ('Albahaca', 'Albahaca'),
        ('Mostaza', 'Mostaza'),
        ('Menta', 'Menta'),
        ('Hierbabuena', 'Hierbabuena'),
    ]
    OPCIONES_SISTEMA = [
        ('PLA', 'Plantinera'),
        ('MAD', 'Maduración'),
        ('VER', 'Vertical Wall'),
    ]
    ESTADOS = [
        ('GER', 'Germinacion'),
        ('VEG', 'Vegetativo'),
        ('FLO', 'Floracion'),
        ('COS', 'Cosecha'),
        ('FIN', 'Finalizado'),
    ]
    OPCIONES_SUBSISTEMA = [
        # Plantinera
        ('PLA-STD', 'Plantinera'),
        ('PLA-MICRO', 'Microgreens'),

        # Maduración
        ('MAD-R1', 'Rack I'),
        ('MAD-R2', 'Rack II'),
        ('MAD-R3', 'Rack III'),
        ('MAD-R4', 'Rack IV'),

        # Vertical wall
        ('VER-1', 'Vertical I'),
        ('VER-2', 'Vertical II'),
    ]
    
    lote_id = models.CharField(max_length=15, unique=True, editable=False, verbose_name="ID de Lote")
    nombre = models.CharField(max_length=50, choices=OPCIONES_CULTIVO)
    variedad = models.CharField(max_length=100, blank=True)
    fecha_siembra = models.DateField(default=timezone.now)
    sistema_produccion = models.CharField(max_length=3, choices=OPCIONES_SISTEMA, default='PLA')
    subsistema = models.CharField(max_length=10, choices=OPCIONES_SUBSISTEMA, default='PLA-STD', verbose_name="Ubicación")
    cantidad_bandejas = models.PositiveIntegerField(default=1)
    fecha_traspaso_real = models.DateField(null=True, blank=True, verbose_name="Fecha de traspaso")
    estado = models.CharField(max_length=3, choices=ESTADOS, default='GER')
    detalles = models.TextField(null=True, blank=True)

    # Generación de ID único para cada cultivo. Formato del ID: añomes-3 primera letras del cultivo-código único (ej: 2602-LEC-A1B2)
    def save(self, *args, **kwargs):
        # Si el lote está vacío, significa que es un cultivo nuevo
        if not self.lote_id:
            # Detectar el formato de la fecha desde el HTML y se convierte
            if isinstance(self.fecha_siembra, str):
                fecha_obj = datetime.strptime(self.fecha_siembra, '%Y-%m-%d')
            else:
                fecha_obj = self.fecha_siembra

            # Obtener año y mes"
            año_mes = fecha_obj.strftime("%m%y")
            # Obtener las primeras 3 letras del cultivo en mayúsculas
            prefijo_cultivo = self.nombre[:3].upper()
            # Generar 4 caracteres aleatorios seguros
            aleatorio = uuid.uuid4().hex[:4].upper()
            # Armar el ID final
            self.lote_id = f"{año_mes}-{prefijo_cultivo}-{aleatorio}"
        
        # Guardar el objeto en base de datos
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.lote_id} - {self.nombre}"


    @property
    def fecha_traspaso(self):
        """Calcula la fecha estimada de traspaso a la siguiente etapa según el estado actual."""
        if self.sistema_produccion == 'PLA' and self.fecha_siembra:
            return self.fecha_siembra + timedelta(days=15)
        return None

    def __str__(self):
        return f"{self.nombre} - {self.variedad} ({self.get_sistema_produccion_display()})"


class Insumo(models.Model):
    UNIDADES = [
        ('L', 'Litros'),
        ('ML', 'Mililitros'),
        ('KG', 'Kilogramos'),
        ('G', 'Gramos'),
        ('UN', 'Unidades'),
    ]
    nombre = models.CharField(max_length=100)
    stock_actual = models.FloatField(default=0)
    unidad = models.CharField(max_length=2, choices=UNIDADES)
    stock_minimo = models.FloatField(default=5)

    def __str__(self):
        return f"{self.nombre} ({self.stock_actual} {self.unidad})"


class Tarea(models.Model):
    PRIORIDAD_CHOICES = [
        ('ALTA', '🔴 Crítica/Urgente'),
        ('MEDIA', '🟡 Rutina/Importante'),
        ('BAJA', '🔵 Mantenimiento/Baja'),
    ]
    SUBSISTEMA_CHOICES = [
        ('GENERAL', 'Sistema General'),
        # Plantinera
        ('PLA-STD', 'Plantinera'),
        ('PLA-MICRO', 'Microgreens'),

        # Maduración
        ('MAD-R1', 'Maduración Rack I'),
        ('MAD-R2', 'Maduración Rack II'),
        ('MAD-R3', 'Maduración Rack III'),
        ('MAD-R4', 'Maduración Rack IV'),

        # Vertical wall
        ('VER-1', 'Vertical I'),
        ('VER-2', 'Vertical II'),
    ]

    titulo = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='MEDIA')
    subsistema = models.CharField(max_length=20, choices=SUBSISTEMA_CHOICES, default='PLA-STD')
    cultivo_asociado = models.ForeignKey(Cultivo, on_delete=models.SET_NULL, null=True, blank=True)
    completada = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_completada = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        estado = "✅" if self.completada else "⏳"
        return f"{estado} {self.titulo} - {self.get_subsistema_display()}"


class HistorialOperacion(models.Model):
    TIPO_ACCION = [
        ('REGISTRO', 'Nuevo Registro'),
        ('TRASPASO', 'Traspaso de sistema'),
        ('EDICION', 'Edición de datos'),
        ('ELIMINACION', 'Eliminación'),
        ('COSECHA', 'Cosecha realizada'),
    ]

    fecha_hora = models.DateTimeField(default=timezone.now)
    tipo_accion = models.CharField(max_length=20, choices=TIPO_ACCION)
    lote_id_afectado = models.CharField(max_length=20)

    # Campos originales
    cultivo_nombre = models.CharField(max_length=50, null=True, blank=True)
    fecha_siembra_registrada = models.DateField(null=True, blank=True)
    subsistema_registrado = models.CharField(max_length=10, null=True, blank=True)
    cantidad = models.PositiveIntegerField(null=True, blank=True)

    # Registros previos
    cultivo_nombre_anterior = models.CharField(max_length=50, null=True, blank=True)
    subsistema_previo = models.CharField(max_length=20, null=True, blank=True)
    cantidad_anterior = models.PositiveIntegerField(null=True, blank=True)
    fecha_anterior = models.DateField(null=True, blank=True)
    detalles = models.TextField(blank=True, null=True)

    # Registros posteriores
    cultivo_nombre_nuevo = models.CharField(max_length=50, null=True, blank=True)
    subsistema_posterior = models.CharField(max_length=20, null=True, blank=True)
    cantidad_posterior = models.PositiveIntegerField(null=True, blank=True)
    fecha_modificada = models.DateField(null=True, blank=True)

    # Campo específico para traspasos
    fecha_siembra_traspaso = models.DateField(null=True, blank=True)

    # Detalles generales
    detalles = models.TextField(blank=True, null=True)

    # Guardar el porcentaje de éxito en las cosechas
    rendimiento = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.get_tipo_accion_display()} - {self.lote_id_afectado}"