from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import PerfumeRecomendacionForm
from .models import Recomendacion
from perfumes.models import Perfume
from .utils import consultar_clima, construir_prompt, llamar_ia_gemini

@login_required
def formulario_recomendacion(request):
    perfumes = Perfume.objects.filter(usuario=request.user)
    if not perfumes.exists():
        messages.warning(request, "Debes registrar al menos un perfume antes de solicitar una recomendación.")
        return redirect('perfumes:mis_perfumes')

    if request.method == 'POST':
        form = PerfumeRecomendacionForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.usuario = request.user

            # Obtener clima
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

            # Crear prompt y obtener recomendación
            prompt = construir_prompt(obj, perfumes)
            obj.prompt = prompt

            respuesta = llamar_ia_gemini(prompt)
            obj.respuesta_ia = respuesta

            # Por ahora: asignar primer perfume como respuesta simulada
            perfume_sugerido = perfumes.first()
            obj.perfume_recomendado = perfume_sugerido
            obj.explicacion = f"IA sugiere: {perfume_sugerido.nombre} para esta ocasión."

            obj.save()

            return render(request, 'recomendador/resultado.html', {'recomendacion': obj})
    else:
        form = PerfumeRecomendacionForm()

    return render(request, 'recomendador/formulario.html', {'form': form})
