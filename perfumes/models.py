from django.db import models
from django.conf import settings

class Perfume(models.Model):
    CONCENTRACIONES = [
        ('EDT', 'Eau de Toilette'),
        ('EDP', 'Eau de Parfum'),
        ('PARFUM', 'Parfum'),
        ('EXTRAIT', 'Extrait'),
    ]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    marca = models.CharField(max_length=100)
    perfumista = models.CharField(max_length=100, blank=True, null=True)
    concentracion = models.CharField(max_length=10, choices=CONCENTRACIONES)
    imagen = models.ImageField(upload_to='perfumes/', blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} - {self.marca}"
