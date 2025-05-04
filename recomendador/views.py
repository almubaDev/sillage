from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from perfumes.models import Perfume, ColeccionUsuario
from .forms import PerfumeRecomendacionForm
from .utils import consultar_clima, construir_prompt, llamar_ia_gemini


@login_required
def formulario_recomendacion(request):
    perfumes = Perfume.objects.filter(
        id__in=ColeccionUsuario.objects.filter(usuario=request.user).values_list("perfume_id", flat=True)
    )

    if not perfumes.exists():
        messages.warning(request, "Debes registrar al menos un perfume antes de solicitar una recomendación.")
        return redirect('perfumes:mi_coleccion')

    if request.method == 'POST':
        form = PerfumeRecomendacionForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.usuario = request.user

            clima = consultar_clima(
                lat=obj.latitud,
                lon=obj.longitud,
                fecha=obj.fecha_evento,
                hora=obj.hora_evento
            )

            if not clima:
                messages.error(request, "No fue posible obtener el clima para la fecha y lugar seleccionados.")
                return redirect('recomendador:formulario')

            obj.clima_descripcion = clima['descripcion']
            obj.temperatura = clima['temperatura']
            obj.humedad = clima['humedad']

            prompt = construir_prompt(obj, perfumes)
            obj.prompt = prompt
            respuesta = llamar_ia_gemini(prompt)
            obj.respuesta_ia = respuesta

            perfume_sugerido = None
            for perfume in perfumes:
                nombre_slug = slugify(perfume.nombre)
                if nombre_slug in slugify(respuesta):
                    perfume_sugerido = perfume
                    break

            if perfume_sugerido:
                obj.perfume_recomendado = perfume_sugerido
                obj.explicacion = f"La IA recomendó {perfume_sugerido.nombre} como la mejor opción."
            else:
                obj.explicacion = "La IA no mencionó explícitamente un perfume conocido de tu colección."

            obj.save()
            return render(request, 'recomendador/resultado.html', {'recomendacion': obj})
    else:
        form = PerfumeRecomendacionForm()

    return render(request, 'recomendador/formulario.html', {'form': form})
