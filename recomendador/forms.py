from django import forms
from datetime import date, timedelta
from django.utils.translation import gettext_lazy as _
from .models import Recomendacion

class PerfumeRecomendacionForm(forms.ModelForm):
    class Meta:
        model = Recomendacion
        fields = [
            'fecha_evento',
            'hora_evento',
            'lugar_tipo',
            'lugar_descripcion',
            'ocasion',
            'expectativa',
            'vestimenta',
            'latitud',
            'longitud',
            'lugar_nombre',
        ]

        widgets = {
            'fecha_evento': forms.DateInput(attrs={'type': 'date', 'class': 'w-full border rounded px-3 py-2'}),
            'hora_evento': forms.TimeInput(attrs={'type': 'time', 'class': 'w-full border rounded px-3 py-2'}),
            'lugar_tipo': forms.Select(attrs={'class': 'w-full border rounded px-3 py-2'}),
            'lugar_descripcion': forms.Textarea(attrs={
                'maxlength': 150,
                'rows': 3,
                'placeholder': _('Ej: Terraza junto al mar, bastante ventilada.'),
                'class': 'w-full border rounded px-3 py-2'
            }),
            'ocasion': forms.TextInput(attrs={
                'placeholder': _('Ej: Cena formal'),
                'class': 'w-full border rounded px-3 py-2'
            }),
            'expectativa': forms.TextInput(attrs={
                'placeholder': _('Ej: Impresionar a alguien'),
                'class': 'w-full border rounded px-3 py-2'
            }),
            'vestimenta': forms.TextInput(attrs={
                'placeholder': _('Ej: Blazer oscuro, vestido verde, chaqueta de cuero'),
                'class': 'w-full border rounded px-3 py-2'
            }),
            'latitud': forms.HiddenInput(),
            'longitud': forms.HiddenInput(),
            'lugar_nombre': forms.HiddenInput(),
        }

    def clean_fecha_evento(self):
        fecha = self.cleaned_data['fecha_evento']
        hoy = date.today()
        limite = hoy + timedelta(days=5)

        if fecha < hoy:
            raise forms.ValidationError(_("La fecha no puede ser anterior a hoy."))
        if fecha > limite:
            raise forms.ValidationError(_("Solo puedes solicitar recomendaciones dentro de los próximos 5 días."))
        return fecha
