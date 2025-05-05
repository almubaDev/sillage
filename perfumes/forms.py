from django import forms
from .models import Perfume
import json

class PerfumeForm(forms.ModelForm):
    # Campos para texto normal que serán convertidos a JSON
    notas_texto = forms.CharField(
        label="Notas",
        widget=forms.Textarea(attrs={
            'class': 'w-full border rounded px-3 py-2', 
            'rows': 3,
            'placeholder': 'Bergamota, lavanda, vainilla (separar con comas)'
        }),
        required=False
    )
    
    acordes_texto = forms.CharField(
        label="Acordes",
        widget=forms.Textarea(attrs={
            'class': 'w-full border rounded px-3 py-2', 
            'rows': 2,
            'placeholder': 'Cítrico, floral, amaderado (separar con comas)'
        }),
        required=False
    )
    
    class Meta:
        model = Perfume
        fields = ['nombre', 'marca', 'perfumista']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2'}),
            'marca': forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2'}),
            'perfumista': forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2'}),
        }
    
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)
        
        # Si estamos editando un perfume existente, convertir las listas JSON a texto
        if instance:
            if instance.notas:
                self.fields['notas_texto'].initial = ', '.join(instance.notas)
            if instance.acordes:
                self.fields['acordes_texto'].initial = ', '.join(instance.acordes)
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Convertir las notas de texto a lista (JSON)
        notas_texto = cleaned_data.get('notas_texto', '')
        if notas_texto:
            # Dividir por comas y eliminar espacios en blanco
            notas_lista = [item.strip() for item in notas_texto.split(',') if item.strip()]
            cleaned_data['notas'] = notas_lista
        else:
            cleaned_data['notas'] = []
            
        # Convertir los acordes de texto a lista (JSON)
        acordes_texto = cleaned_data.get('acordes_texto', '')
        if acordes_texto:
            # Dividir por comas y eliminar espacios en blanco
            acordes_lista = [item.strip() for item in acordes_texto.split(',') if item.strip()]
            cleaned_data['acordes'] = acordes_lista
        else:
            cleaned_data['acordes'] = []
            
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.notas = self.cleaned_data.get('notas', [])
        instance.acordes = self.cleaned_data.get('acordes', [])
        
        if commit:
            instance.save()
        return instance