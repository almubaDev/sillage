from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-3 py-2 border rounded',
            'placeholder': 'correo@ejemplo.com',
        })
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 border rounded',
            'placeholder': '••••••••',
        })
    )



class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        label="Nombre",
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border rounded',
            'placeholder': 'Tu nombre'
        })
    )
    last_name = forms.CharField(
        label="Apellido",
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border rounded',
            'placeholder': 'Tu apellido'
        })
    )
    # rut = forms.CharField(
    #     label="RUT",
    #     required=True,
    #     widget=forms.TextInput(attrs={
    #         'class': 'w-full px-3 py-2 border rounded',
    #         'placeholder': '11111111-1'
    #     })
    # )
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-3 py-2 border rounded',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 border rounded',
            'placeholder': '••••••••'
        })
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 border rounded',
            'placeholder': '••••••••'
        })
    )
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')