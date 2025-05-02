from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Perfume, ColeccionUsuario
from .forms import PerfumeForm


@login_required
def mi_coleccion(request):
    perfumes = ColeccionUsuario.objects.filter(usuario=request.user).select_related("perfume")
    return render(request, "perfumes/coleccion.html", {"perfumes": perfumes})

@login_required
def buscar_perfumes(request):
    query = request.GET.get("q", "")
    resultados = Perfume.objects.filter(nombre__icontains=query) if query else []
    coleccion_ids = ColeccionUsuario.objects.filter(usuario=request.user).values_list("perfume_id", flat=True)
    return render(request, "perfumes/busqueda.html", {
        "resultados": resultados,
        "query": query,
        "coleccion_ids": coleccion_ids
    })

@login_required
def agregar_a_coleccion(request, perfume_id):
    perfume = get_object_or_404(Perfume, id=perfume_id)
    obj, creado = ColeccionUsuario.objects.get_or_create(usuario=request.user, perfume=perfume)
    if creado:
        messages.success(request, f"{perfume.nombre} fue agregado a tu colección.")
    else:
        messages.info(request, f"{perfume.nombre} ya estaba en tu colección.")
    return redirect("buscar_perfumes")

@login_required
def eliminar_de_coleccion(request, perfume_id):
    perfume = get_object_or_404(Perfume, id=perfume_id)
    ColeccionUsuario.objects.filter(usuario=request.user, perfume=perfume).delete()
    messages.success(request, f"{perfume.nombre} fue eliminado de tu colección.")
    return redirect("buscar_perfumes")

@login_required
def nuevo_perfume(request):
    if request.method == "POST":
        form = PerfumeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfume agregado correctamente.")
            return redirect("buscar_perfumes")
    else:
        form = PerfumeForm()
    return render(request, "perfumes/nuevo.html", {"form": form})
