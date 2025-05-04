from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class Suscripcion(models.Model):
    class TipoSuscripcion(models.TextChoices):
        MENSUAL = 'mensual', _('Mensual con renovación')

    class OrigenPago(models.TextChoices):
        PAYPAL = 'paypal', 'PayPal'
        MANUAL = 'manual', 'Manual'

    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TipoSuscripcion.choices, default=TipoSuscripcion.MENSUAL)
    activo = models.BooleanField(default=True)

    fecha_inicio = models.DateTimeField(default=timezone.now)
    fecha_expiracion = models.DateTimeField(null=True, blank=True)

    consultas_restantes = models.IntegerField(default=30)
    perfumes_maximos = models.IntegerField(default=100)  # Valor por defecto en lugar de null

    renovacion_automatica = models.BooleanField(default=True)  # Por defecto activo

    origen_pago = models.CharField(max_length=20, choices=OrigenPago.choices, default=OrigenPago.PAYPAL)
    referencia_pago = models.CharField(max_length=100, null=True, blank=True)
    
    # Campos para PayPal
    paypal_subscription_id = models.CharField(max_length=100, null=True, blank=True, unique=True)
    paypal_plan_id = models.CharField(max_length=100, null=True, blank=True)
    ultima_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.usuario} → {self.get_tipo_display()}"

    def es_ilimitado(self):
        return self.perfumes_maximos is None

    def tiene_consultas(self):
        return self.consultas_restantes is None or self.consultas_restantes > 0