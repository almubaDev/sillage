import requests
import calendar
from datetime import datetime,timedelta
from django.conf import settings
from django.utils.translation import get_language


# ---------------------------------------------------
# 🔁 CONSULTAR CLIMA desde OpenWeatherMap
# ---------------------------------------------------
def consultar_clima(lat, lon, fecha, hora):
    api_key = settings.OPENWEATHER_API_KEY
    dt_objetivo = datetime.combine(fecha, hora)
    url = (
        f"https://api.openweathermap.org/data/2.5/forecast?"
        f"lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=es"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        bloques = data.get('list', [])
        if not bloques:
            return None

        # Elegimos el bloque más cercano en tiempo
        mejor_bloque = min(
            bloques,
            key=lambda b: abs(datetime.strptime(b['dt_txt'], "%Y-%m-%d %H:%M:%S") - dt_objetivo)
        )

        return {
            'descripcion': mejor_bloque['weather'][0]['description'],
            'temperatura': mejor_bloque['main']['temp'],
            'humedad': mejor_bloque['main']['humidity']
        }

    except Exception as e:
        print("❌ Error al consultar clima:", e)
        return None

# ---------------------------------------------------
# 🧠 CONSTRUIR PROMPT PARA GEMINI
# ---------------------------------------------------

def construir_prompt(obj, perfumes_queryset):
    idioma = get_language()

    # Estación del año
    mes = obj.fecha_evento.month
    estaciones = {
        1: "verano", 2: "verano", 3: "otoño", 4: "otoño",
        5: "invierno", 6: "invierno", 7: "invierno",
        8: "primavera", 9: "primavera", 10: "primavera",
        11: "verano", 12: "verano"
    }
    estacion = estaciones.get(mes, "desconocida")

    # Momento del día
    hora = obj.hora_evento.hour
    if hora < 12:
        momento_dia = "mañana"
    elif hora < 19:
        momento_dia = "tarde"
    else:
        momento_dia = "noche"

    # Formatear perfumes
    perfumes_formateados = ""
    for p in perfumes_queryset:
        perfumes_formateados += f"- {p.nombre} ({p.marca})"
        if p.perfumista:
            perfumes_formateados += f", perfumista: {p.perfumista}"
        if getattr(p, "concentracion", None):
            perfumes_formateados += f", concentración: {p.concentracion}"
        if p.notas:
            perfumes_formateados += f"\n  Notas: {', '.join(p.notas)}"
        if p.acordes:
            perfumes_formateados += f"\n  Acordes: {', '.join(p.acordes)}"
        perfumes_formateados += "\n\n"

    # Prompt base en español (puedes agregar aquí estructura multilenguaje si lo necesitas)
    prompt = f"""
Eres un experto perfumista con conocimiento profundo en notas olfativas, comportamiento molecular, estaciones, climatología, emociones humanas y códigos sociales. Tu tarea es recomendar UN SOLO perfume de la colección personal del usuario que sea óptimo para su contexto ambiental, emocional y estético.

## DATOS CONTEXTUALES DEL EVENTO
- 📍 Ubicación: {obj.lugar_nombre} ({obj.lugar_tipo})
- 🏙️ Descripción del entorno: {obj.lugar_descripcion}
- 🕒 Fecha y hora: {obj.fecha_evento} {obj.hora_evento}
- 🌡️ Clima estimado: {obj.clima_descripcion}, {obj.temperatura}°C, humedad {obj.humedad}%
- 🍂 Estación del año: {estacion}
- ☀️ Momento del día: {momento_dia}
- 👕 Vestimenta: {obj.vestimenta}
- 🎯 Ocasión: {obj.ocasion}
- 🧠 Expectativa emocional: {obj.expectativa}

## PERFUMES DISPONIBLES

Cada perfume incluye: nombre, marca, perfumista, concentración, lista de notas (sin orden) y acordes dominantes.

{perfumes_formateados}

## FUNDAMENTOS DE SELECCIÓN

1. Analiza el entorno (clima, estación, humedad, hora) y determina qué tipos de notas suelen adaptarse mejor (cítricas, florales, amaderadas, balsámicas, etc.)
2. Evalúa los perfumes disponibles uno por uno. Determina cuáles contienen notas o acordes compatibles con las condiciones ambientales.
3. Considera la concentración del perfume (Parfum, EDP, EDT) y si su intensidad es adecuada según el tipo de lugar (abierto o cerrado) y condiciones climáticas.
4. Aplica un segundo filtro estético y emocional: estilo de vestimenta, naturaleza del evento, y expectativa emocional del usuario.
5. Si no hay coincidencias evidentes por notas, selecciona el perfume que mejor se alinee con la dimensión emocional y social del evento.

## FORMATO DE RESPUESTA

Tu respuesta debe iniciar con:

**“Recomiendo usar: [NOMBRE DEL PERFUME]”**

Y debe contener, en ese orden:

1. Análisis Ambiental  
2. Perfil del Perfume Elegido  
3. Justificación Estética y Emocional  
4. Recomendación de Aplicación (número de sprays, zonas del cuerpo)
"""

    print("📤 PROMPT ENVIADO A GEMINI:\n" + "-" * 60 + "\n" + prompt + "\n" + "-" * 60)
    return prompt






# ---------------------------------------------------
# 🤖 LLAMAR GEMINI API (Google Generative Language)
# ---------------------------------------------------
def llamar_ia_gemini(prompt):
    api_key = settings.GEMINI_API_KEY
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    try:
        res = requests.post(url, json=payload)
        res.raise_for_status()
        data = res.json()
        print("📥 RESPUESTA COMPLETA DE GEMINI:\n", data)
        return data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'No se pudo generar una recomendación en este momento.')
    except Exception as e:
        print("❌ Error al llamar Gemini:", e)
        return "No se pudo generar una recomendación en este momento."
