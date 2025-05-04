from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from perfumes.models import Perfume, ColeccionUsuario
from .forms import PerfumeRecomendacionForm
from .utils import consultar_clima, construir_prompt, llamar_ia_gemini
import re

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

            prompt = construir_prompt(obj, perfumes, request.user.email)
            obj.prompt = prompt
            respuesta = llamar_ia_gemini(prompt)
            obj.respuesta_ia = respuesta

            # Método mejorado para identificar el perfume recomendado
            perfume_sugerido = None
            
            # Buscar patrones específicos para la recomendación principal
            # Patrones para buscar al principio de la respuesta o después de asteriscos
            primary_patterns = [
                r'^\s*\*\*([^*\n]+)\*\*', # Texto entre ** al inicio de la respuesta
                r'^\s*([^\n]+)\n', # Primera línea (asumiendo que es el título)
            ]
            
            for pattern in primary_patterns:
                match = re.search(pattern, respuesta)
                if match:
                    nombre_candidato = match.group(1).strip()
                    # Evitar falsos positivos (como "Recomendación para...")
                    if not any(x in nombre_candidato.lower() for x in ["recomendación", "alternativa", "recomendado", "motivo"]):
                        for perfume in perfumes:
                            if slugify(perfume.nombre) in slugify(nombre_candidato):
                                perfume_sugerido = perfume
                                break
                        if perfume_sugerido:
                            break
            
            # Si no encontramos un perfume con los patrones principales, buscar menciones explícitas
            if not perfume_sugerido:
                explicit_patterns = [
                    r'recomiendo(?:\s+usar)?:\s*([^\n\.]+)',
                    r'perfume\s+recomendado\s+final[^\n:]*:\s*([^\n\.]+)',
                    r'mejor\s+opción[^\n:]*:\s*([^\n\.]+)',
                ]
                
                for pattern in explicit_patterns:
                    match = re.search(pattern, respuesta, re.IGNORECASE)
                    if match:
                        nombre_candidato = match.group(1).strip()
                        for perfume in perfumes:
                            if slugify(perfume.nombre) in slugify(nombre_candidato):
                                perfume_sugerido = perfume
                                break
                        if perfume_sugerido:
                            break
            
            # Si todavía no tenemos un perfume, usar el método anterior como fallback
            if not perfume_sugerido:
                # Excluir explícitamente perfumes mencionados como "alternativa"
                alternativa_match = re.search(r'alternativa[^:]*:\s*([^\n\.]+)', respuesta, re.IGNORECASE)
                alternativa_nombre = alternativa_match.group(1).strip() if alternativa_match else ""
                
                for perfume in perfumes:
                    nombre_slug = slugify(perfume.nombre)
                    if nombre_slug in slugify(respuesta):
                        # Verificar que no sea la alternativa
                        if not alternativa_nombre or nombre_slug not in slugify(alternativa_nombre):
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