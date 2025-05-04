from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils.text import slugify
from unidecode import unidecode
from .models import Perfume, ColeccionUsuario
from .forms import PerfumeForm


@login_required
def mi_coleccion(request):
    perfumes = ColeccionUsuario.objects.filter(usuario=request.user).select_related("perfume")
    return render(request, "perfumes/coleccion.html", {"perfumes": perfumes})

@login_required
def buscar_perfumes(request):
    query = request.GET.get("q", "").strip()
    marca = request.GET.get("marca", "").strip()
    acorde = request.GET.get("acorde", "").strip()

    perfumes = Perfume.objects.none()  # ← nunca cargar todos por defecto

    if query or marca or acorde:
        perfumes = Perfume.objects.all()

        if query:
            normalized_q = slugify(unidecode(query))
            perfumes = perfumes.filter(
                Q(nombre__icontains=query) |
                Q(nombre__icontains=normalized_q.replace("-", " ")) |
                Q(nombre__icontains=normalized_q)
            )

        if marca:
            normalized_m = slugify(unidecode(marca))
            perfumes = perfumes.filter(
                Q(marca__icontains=marca) |
                Q(marca__icontains=normalized_m.replace("-", " ")) |
                Q(marca__icontains=normalized_m)
            )

        if acorde:
            perfumes = perfumes.filter(acordes__icontains=acorde)

        perfumes = perfumes.distinct()

    coleccion_ids = ColeccionUsuario.objects.filter(
        usuario=request.user
    ).values_list("perfume_id", flat=True)

    return render(request, "perfumes/busqueda.html", {
        "resultados": perfumes,
        "query": query,
        "marca": marca,
        "acorde": acorde,
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

    next_url = request.POST.get("next")
    if next_url:
        return redirect(next_url)
    return redirect("perfumes:buscar_perfumes")

@login_required
def eliminar_de_coleccion(request, perfume_id):
    perfume = get_object_or_404(Perfume, id=perfume_id)
    ColeccionUsuario.objects.filter(usuario=request.user, perfume=perfume).delete()
    messages.success(request, f"{perfume.nombre} fue eliminado de tu colección.")
    return redirect("perfumes:mi_coleccion")

@login_required
def nuevo_perfume(request):
    if request.method == "POST":
        form = PerfumeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfume agregado correctamente.")
            return redirect("perfumes:mi_coleccion")
    else:
        form = PerfumeForm()
    return render(request, "perfumes/nuevo.html", {"form": form})
