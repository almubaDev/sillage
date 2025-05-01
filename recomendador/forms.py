from django import forms
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
                'maxlength': 150, 'rows': 3,
                'class': 'w-full border rounded px-3 py-2',
                'placeholder': 'Ej: Terraza junto al mar, bastante ventilada.'
            }),
            'ocasion': forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2', 'placeholder': 'Ej: Cena formal'}),
            'expectativa': forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2', 'placeholder': 'Ej: Impresionar a alguien'}),
            'vestimenta': forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2', 'placeholder': 'Ej: Blazer oscuro, perfume elegante'}),
            'latitud': forms.HiddenInput(),
            'longitud': forms.HiddenInput(),
            'lugar_nombre': forms.HiddenInput(),
        }
