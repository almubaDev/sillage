from django import forms
from .models import Suscripcion

class SuscripcionForm(forms.ModelForm):
    class Meta:
        model = Suscripcion
        fields = [
            'tipo', 'fecha_inicio', 'fecha_expiracion',
            'consultas_restantes', 'perfumes_maximos',
            'renovacion_automatica', 'origen_pago', 'referencia_pago'
        ]