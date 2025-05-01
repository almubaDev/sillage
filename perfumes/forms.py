from django import forms
from .models import Perfume

class PerfumeForm(forms.ModelForm):
    class Meta:
        model = Perfume
        fields = ['nombre', 'marca', 'perfumista', 'concentracion', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2', 'placeholder': 'Nombre del perfume'}),
            'marca': forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2', 'placeholder': 'Marca'}),
            'perfumista': forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2', 'placeholder': 'Perfumista (opcional)'}),
            'concentracion': forms.Select(attrs={'class': 'w-full border rounded px-3 py-2'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'w-full'}),
        }
