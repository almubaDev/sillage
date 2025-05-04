# administrador/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Suscripcion
from .forms import SuscripcionForm
from django.contrib.auth.decorators import login_required

@login_required
def lista_suscripciones(request):
    suscripciones = Suscripcion.objects.filter(usuario=request.user)
    return render(request, 'administrador/lista_suscripciones.html', {'suscripciones': suscripciones})

@login_required
def crear_suscripcion(request):
    if request.method == 'POST':
        form = SuscripcionForm(request.POST)
        if form.is_valid():
            nueva = form.save(commit=False)
            nueva.usuario = request.user
            nueva.save()
            return redirect('administrador:lista_suscripciones')
    else:
        form = SuscripcionForm()
    return render(request, 'administrador/formulario_suscripcion.html', {'form': form})

@login_required
def editar_suscripcion(request, pk):
    suscripcion = get_object_or_404(Suscripcion, pk=pk, usuario=request.user)
    if request.method == 'POST':
        form = SuscripcionForm(request.POST, instance=suscripcion)
        if form.is_valid():
            form.save()
            return redirect('administrador:lista_suscripciones')
    else:
        form = SuscripcionForm(instance=suscripcion)
    return render(request, 'administrador/formulario_suscripcion.html', {'form': form})

@login_required
def eliminar_suscripcion(request, pk):
    suscripcion = get_object_or_404(Suscripcion, pk=pk, usuario=request.user)
    if request.method == 'POST':
        suscripcion.delete()
        return redirect('administrador:lista_suscripciones')
    return render(request, 'administrador/confirmar_eliminar.html', {'suscripcion': suscripcion})
