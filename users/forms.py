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
        fields = ('email',)
