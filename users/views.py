from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CustomLoginForm, CustomUserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.urls import reverse

@login_required
def perfil_view(request):
    # Obtener el usuario directamente de la base de datos
    from django.contrib.auth import get_user_model
    User = get_user_model()
    usuario_actual = User.objects.get(pk=request.user.pk)
    
    # Para debugging - puedes quitar estos prints cuando todo funcione correctamente
    from django.utils import translation
    current_language = translation.get_language()
    print(f"Idioma actual: {current_language}")
    print(f"LANGUAGE_CODE en request: {request.LANGUAGE_CODE if hasattr(request, 'LANGUAGE_CODE') else 'No disponible'}")
    print(f"Estado de suscripción: {usuario_actual.suscrito}")
    
    redirect_to = request.GET.get('next', request.path)
    
    if request.method == 'POST':
        if 'unsubscribe' in request.POST:
            usuario_actual.suscrito = False
            usuario_actual.save()
            # Cambiado a español (idioma base)
            messages.success(request, _("Te has dado de baja correctamente."))
            return redirect('users:perfil')

    return render(request, 'users/perfil.html', {
        'usuario': usuario_actual,
        'redirect_to': redirect_to
    })

class CustomLoginView(LoginView):
    authentication_form = CustomLoginForm
    template_name = 'users/login.html'

    def get_success_url(self):
        return reverse_lazy('users:perfil')

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('users:login')

class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:perfil')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)  # Autologin tras registro
        return response