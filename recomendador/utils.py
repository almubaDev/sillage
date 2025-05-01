import requests
from datetime import datetime
from django.utils.translation import get_language

# ---------------------------------------------------
# 🔁 CONSULTAR CLIMA desde OpenWeatherMap
# ---------------------------------------------------
def consultar_clima(lat, lon, fecha, hora):
    """
    Consulta el clima para lat/lon en fecha y hora específica.
    """
    api_key = "TU_API_KEY_OPENWEATHER"  # ← Reemplazar por tu clave real
    dt_objetivo = datetime.combine(fecha, hora)
    url = (
        f"https://api.openweathermap.org/data/2.5/forecast?"
        f"lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=es"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        objetivo_str = dt_objetivo.strftime("%Y-%m-%d %H:%M:00")
        bloque = next(
            (item for item in data['list'] if item['dt_txt'] == objetivo_str),
            None
        )

        if bloque:
            return {
                'descripcion': bloque['weather'][0]['description'],
                'temperatura': bloque['main']['temp'],
                'humedad': bloque['main']['humidity']
            }

    except Exception as e:
        print("❌ Error al consultar clima:", e)

    return None

# ---------------------------------------------------
# 🧠 CONSTRUIR PROMPT PARA LA IA
# ---------------------------------------------------
def construir_prompt(obj, perfumes_queryset):
    """
    Arma el texto a enviar a la IA con idioma automático.
    """
    idioma = get_language()
    lang_intro = {
        'es': "Responde en español.",
        'en': "Respond in English.",
    }.get(idioma, "Respond in English.")

    perfumes_texto = "\n".join(
        f"- {p.nombre} ({p.marca})" for p in perfumes_queryset
    )

    return f"""
{lang_intro}

Tengo una colección de perfumes y necesito una recomendación personalizada. Aquí está el contexto:

📍 Lugar: {obj.lugar_nombre} ({obj.lugar_tipo})
📝 Descripción: {obj.lugar_descripcion}
🕒 Fecha y hora: {obj.fecha_evento} {obj.hora_evento}
🌡️ Clima estimado: {obj.clima_descripcion}, {obj.temperatura}°C, humedad {obj.humedad}%
👕 Vestimenta: {obj.vestimenta}
🎯 Ocasión: {obj.ocasion}
🧠 Expectativa emocional: {obj.expectativa}

Perfumes disponibles en la colección:
{perfumes_texto}

Por favor, selecciona el mejor perfume de la lista y explica por qué es adecuado.
"""

# ---------------------------------------------------
# 🤖 LLAMADA A LA IA (simulada)
# ---------------------------------------------------
def llamar_ia_gemini(prompt):
    """
    Envía el prompt a Gemini. Actualmente simulado.
    """
    # En versión real, aquí conectarías con Gemini API.
    return "Según el contexto, recomendaría el perfume más versátil de tu colección para condiciones moderadas, ideal para causar una impresión duradera."
