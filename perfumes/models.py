from django.db import models
from django.conf import settings

class Perfume(models.Model):
    nombre = models.CharField(max_length=150)
    marca = models.CharField(max_length=100)
    notas = models.JSONField()  # Lista combinada de top/middle/base
    acordes = models.JSONField()  # mainaccord1-5
    perfumista = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} - {self.marca}"

class ColeccionUsuario(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    perfume = models.ForeignKey(Perfume, on_delete=models.CASCADE)
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'perfume')

    def __str__(self):
        return f"{self.usuario} → {self.perfume}"
