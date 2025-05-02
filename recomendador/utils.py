import requests
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
    lang_intro = {
        'es': "Responde en español.",
        'en': "Respond in English.",
    }.get(idioma, "Respond in English.")

    perfumes_texto = "\n".join([
        f"- {p.nombre} ({p.marca})" +
        (f", perfumista: {p.perfumista}" if p.perfumista else "") +
        (f", {p.concentracion}" if p.concentracion else "")
        for p in perfumes_queryset
    ])

    prompt = f"""{lang_intro}

Tengo una colección de perfumes. Quiero que me ayudes a elegir el más adecuado para una situación específica.

Por favor, considera cuidadosamente todos estos elementos antes de tomar una decisión:

📍 Lugar: {obj.lugar_nombre} ({obj.lugar_tipo})
📝 Descripción del entorno: {obj.lugar_descripcion}
🕒 Fecha y hora: {obj.fecha_evento} {obj.hora_evento}
🌡️ Clima estimado: {obj.clima_descripcion}, {obj.temperatura}°C, humedad {obj.humedad}%
👕 Vestimenta: {obj.vestimenta}
🎯 Ocasión: {obj.ocasion}
🧠 Expectativa emocional: {obj.expectativa}

Perfumes disponibles en mi colección:

{perfumes_texto}

Obtén las notas principales (de salida, corazón y fondo) de cada perfume listado utilizando tu conocimiento general sobre perfumería.

Basado en todo lo anterior, selecciona un solo perfume de la lista que consideres el más adecuado.

Empieza tu respuesta con una frase clara como:
“Recomiendo usar: [nombre del perfume]”

Luego, justifica por qué elegiste ese perfume según las condiciones del lugar, el clima, la vestimenta, la ocasión y la expectativa emocional.

No describas los otros perfumes. No repitas la lista. Sé directo y conciso.
"""

    print("📤 PROMPT ENVIADO A GEMINI:\n" + "-"*60 + "\n" + prompt + "\n" + "-"*60)
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
