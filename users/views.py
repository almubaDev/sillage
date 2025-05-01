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
    if request.method == 'POST':
        if 'unsubscribe' in request.POST:
            request.user.suscrito = False
            request.user.save()
            messages.success(request, _("You have unsubscribed successfully."))
            return redirect('users:perfil')

    return render(request, 'users/perfil.html', {'usuario': request.user})



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
