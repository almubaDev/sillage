from django.db import models
from django.conf import settings
from perfumes.models import Perfume

class Recomendacion(models.Model):
    # Usuario y momento
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha_evento = models.DateField()
    hora_evento = models.TimeField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    # Lugar
    lugar_tipo = models.CharField(max_length=10, choices=[('abierto', 'Abierto'), ('cerrado', 'Cerrado')])
    lugar_descripcion = models.CharField(max_length=150)
    lugar_nombre = models.CharField(max_length=100)  # Ej: "Parque Bicentenario, Vitacura"
    latitud = models.FloatField()
    longitud = models.FloatField()

    # Contexto del evento
    ocasion = models.CharField(max_length=100)       # ← texto libre
    expectativa = models.CharField(max_length=100)   # ← texto libre
    vestimenta = models.CharField(max_length=100)

    # Clima
    clima_descripcion = models.CharField(max_length=100)
    temperatura = models.FloatField()
    humedad = models.FloatField()

    # IA
    prompt = models.TextField()
    respuesta_ia = models.TextField()

    # Resultado final
    perfume_recomendado = models.ForeignKey(Perfume, on_delete=models.SET_NULL, null=True, blank=True)
    explicacion = models.TextField(blank=True)

    def __str__(self):
        return f"{self.usuario.email} – {self.lugar_nombre} – {self.fecha_evento} {self.hora_evento}"
