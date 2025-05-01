from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Perfume
from .forms import PerfumeForm

@login_required
def mis_perfumes(request):
    perfumes = Perfume.objects.filter(usuario=request.user).order_by('-id')

    form = PerfumeForm()

    if request.method == 'POST':
        form = PerfumeForm(request.POST, request.FILES)
        if form.is_valid():
            perfume = form.save(commit=False)
            perfume.usuario = request.user
            perfume.save()
            return redirect('perfumes:mis_perfumes')

    return render(request, 'perfumes/coleccion.html', {
        'perfumes': perfumes,
        'form': form,
    })

@login_required
def eliminar_perfume(request, pk):
    perfume = get_object_or_404(Perfume, pk=pk, usuario=request.user)
    perfume.delete()
    return redirect('perfumes:mis_perfumes')
