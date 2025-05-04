import requests
import calendar
import random
from datetime import datetime,timedelta
from django.conf import settings
from django.utils.translation import get_language
from django.utils.text import slugify


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


def construir_prompt(obj, perfumes_queryset, email_usuario=None):
    idioma = get_language()

    lang_intro = {
        'es': "Responde en español.",
        'en': "Respond in English.",
    }.get(idioma, "Respond in English.")

    # Determinar estación del año
    mes = obj.fecha_evento.month
    estaciones = {
        1: "verano", 2: "verano", 3: "otoño", 4: "otoño",
        5: "invierno", 6: "invierno", 7: "invierno",
        8: "primavera", 9: "primavera", 10: "primavera",
        11: "verano", 12: "verano"
    }
    estacion = estaciones.get(mes, "desconocida")

    # Determinar momento del día
    hora = obj.hora_evento.hour
    momento_dia = "mañana" if hora < 12 else "tarde" if hora < 19 else "noche"

    # Mezclar perfumes aleatoriamente para evitar sesgos
    perfumes_lista = list(perfumes_queryset)
    random.shuffle(perfumes_lista)  # 🔁 clave para evitar el sesgo por orden
    
    # Crear dos grupos de perfumes para análisis imparcial
    mitad = len(perfumes_lista) // 2
    grupo1 = perfumes_lista[:mitad]
    grupo2 = perfumes_lista[mitad:]

    # Formatear grupos de perfumes
    def formatear_grupo(grupo):
        return "\n".join([
            f"- {p.nombre.title()} ({p.marca.title()})"
            + (f", perfumista: {p.perfumista}" if p.perfumista else "")
            + (f", acordes: {', '.join(p.acordes)}" if p.acordes else "")
            + (f", notas: {', '.join(p.notas)}" if p.notas else "")
            for p in grupo
        ])

    perfumes_grupo1 = formatear_grupo(grupo1)
    perfumes_grupo2 = formatear_grupo(grupo2)

    # Instrucción para olvidar recomendaciones previas si hay email
    olvido_instruccion = ""
    if email_usuario:
        olvido_instruccion = f"""
## IMPORTANTE - OLVIDAR RECOMENDACIONES PREVIAS
Olvida cualquier recomendación que hayas hecho anteriormente al usuario con correo {email_usuario}. 
Analiza este caso como completamente nuevo y único, sin usar patrones o decisiones anteriores como referencia.
"""

    prompt = f"""{lang_intro}

Eres un experto perfumista con conocimiento profundo en notas olfativas, comportamiento molecular, estaciones, clima y códigos sociales. Tu tarea es recomendar el perfume más adecuado de la colección del usuario para su contexto específico.

{olvido_instruccion}

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

## PERFUMES DISPONIBLES - GRUPO A
{perfumes_grupo1}

## PERFUMES DISPONIBLES - GRUPO B
{perfumes_grupo2}

## PROCESO DE FILTRADO SECUENCIAL
Sigue ESTRICTAMENTE este orden de filtrado, descartando perfumes en cada paso:

1. POR ESTACIÓN: Filtra perfumes apropiados para {estacion}
2. POR CLIMA: De los anteriores, filtra por compatibilidad con {obj.temperatura}°C y {obj.humedad}% de humedad
3. POR LUGAR: De los anteriores, filtra por idoneidad para {obj.lugar_tipo} ({obj.lugar_descripcion})
4. POR EXPECTATIVA: De los anteriores, filtra por alineación con expectativa de {obj.expectativa}
5. POR VESTIMENTA: De los anteriores, filtra por armonía con {obj.vestimenta}
6. POR MOMENTO: Finalmente, filtra por idoneidad para {momento_dia}

## INSTRUCCIONES CRÍTICAS
- Realiza TODO el proceso de filtrado ANTES de elegir tu recomendación final
- Solo después de completar los 6 filtros, elige el PERFUME RECOMENDADO FINAL
- Una vez elegido tu PERFUME RECOMENDADO FINAL, no cambies esta elección por ningún motivo
- NO menciones la palabra "RECOMENDACIÓN" o "RECOMENDADO" al principio de tu respuesta
- Para evitar confusiones, inicia tu respuesta SOLO con el nombre del perfume recomendado, nada más

## FORMATO DE RESPUESTA

Tu respuesta debe seguir EXACTAMENTE esta estructura:

1. PRIMERA LÍNEA: El nombre del perfume recomendado (solo el nombre, sin asteriscos ni otra palabra)
2. SEGUNDA LÍNEA: La marca del perfume recomendado 
3. A partir de la tercera línea: Explicación clara sobre por qué este perfume es ideal (3-4 frases)
4. Luego: Recomendación de aplicación (1 frase)
5. Al final: "Alternativa: [NOMBRE ALTERNATIVO]" seguido de una breve explicación

EJEMPLO DE INICIO DE RESPUESTA:
Aventus
Creed
Este perfume es ideal para la ocasión porque...

IMPORTANTE: Tu recomendación principal debe ser consistente a lo largo de todo el texto. No menciones ni defiendas otro perfume como principal.
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
