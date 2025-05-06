from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class Suscripcion(models.Model):
    # Relación con el usuario
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Estado básico
    activo = models.BooleanField(default=True)
    
    # Fechas importantes
    fecha_inicio = models.DateTimeField(default=timezone.now)
    fecha_expiracion = models.DateTimeField(null=True, blank=True)
    fecha_ultima_renovacion = models.DateTimeField(default=timezone.now)
    
    # Información de pago básica
    origen_pago = models.CharField(max_length=100, help_text="Origen del pago (ej: PayPal, transferencia, etc)")
    referencia_pago = models.CharField(max_length=100, null=True, blank=True)
    
    # Información económica
    monto = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, 
                               help_text="Monto de la suscripción")
    moneda = models.CharField(max_length=3, default="USD", 
                             help_text="Moneda de la suscripción (USD, EUR, CLP, etc.)")
    
    # Configuración
    renovacion_automatica = models.BooleanField(default=True)
    
    # Auditoría
    ultima_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.usuario} - {'Activa' if self.activo else 'Inactiva'}"

    def renovar(self):
        """
        Renueva la suscripción, actualizando fechas y restableciendo consultas del usuario
        """
        # Actualizar fechas
        self.fecha_ultima_renovacion = timezone.now()
        if self.fecha_expiracion and self.fecha_expiracion > timezone.now():
            # Si aún no ha expirado, sumar un mes a la fecha actual de expiración
            self.fecha_expiracion = self.fecha_expiracion + timezone.timedelta(days=30)
        else:
            # Si ya expiró, calcular desde hoy
            self.fecha_expiracion = timezone.now() + timezone.timedelta(days=30)
        
        # Reestablecer consultas del usuario
        self.usuario.consultas_restantes = 30
        self.usuario.save()
        
        # Asegurar que esté activa
        self.activo = True
        self.save()
        
    def cancelar(self):
        """
        Cancela la suscripción
        """
        self.activo = False
        self.renovacion_automatica = False
        self.save()
        
        # Actualizar usuario
        self.usuario.suscrito = False
        # No reseteamos las consultas_restantes para que pueda usar las que le quedan
        self.usuario.save()


class HistorialPago(models.Model):
    # Referencias básicas
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                               related_name='pagos')
    suscripcion = models.ForeignKey(Suscripcion, on_delete=models.CASCADE, 
                                   related_name='pagos', null=True, blank=True)
    
    # Información del pago
    fecha_pago = models.DateTimeField(default=timezone.now)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    moneda = models.CharField(max_length=3, default="USD")
    
    # Método y referencia
    metodo_pago = models.CharField(max_length=100, help_text="Método de pago utilizado (PayPal, transferencia, etc.)")
    referencia = models.CharField(max_length=255, blank=True, null=True, 
                                help_text="Número de referencia o ID de transacción")
    
    # Estado del pago
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('completado', 'Completado'),
        ('fallido', 'Fallido'),
        ('reembolsado', 'Reembolsado'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='completado')
    
    # Notas adicionales (texto simple)
    notas = models.TextField(blank=True, null=True, 
                           help_text="Información adicional sobre el pago")
    
    # Campos de auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.usuario} - {self.monto} {self.moneda} - {self.fecha_pago.date()}"