from django import forms
from .models import Perfume

class PerfumeForm(forms.ModelForm):
    class Meta:
        model = Perfume
        fields = ['nombre', 'marca', 'notas', 'acordes', 'perfumista']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2'}),
            'marca': forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2'}),
            'notas': forms.Textarea(attrs={'class': 'w-full border rounded px-3 py-2', 'rows': 3}),
            'acordes': forms.Textarea(attrs={'class': 'w-full border rounded px-3 py-2', 'rows': 2}),
            'perfumista': forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2'}),
        }
