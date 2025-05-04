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


def construir_prompt(obj, perfumes_queryset):
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
    
    # Crear dos grupos de perfumes para forzar análisis imparcial
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

    prompt = f"""{lang_intro}

Eres un experto perfumista con conocimiento profundo en notas olfativas, comportamiento molecular, estaciones, clima y códigos sociales. Tu tarea es recomendar UN SOLO perfume de la colección personal del usuario que sea óptimo para su contexto ambiental, emocional y estético.

## PROTOCOLO DE ANÁLISIS IMPARCIAL
**PROHIBIDO considerar:**
- Popularidad de la marca
- Reconocimiento de nombres comerciales
- Precios o valor de mercado
- Éxito de ventas histórico
- Prestigio de marcas o perfumistas

**OBLIGATORIO analizar EXCLUSIVAMENTE:**
- Notas aromáticas específicas
- Acordes dominantes
- Comportamiento según temperatura y humedad
- Compatibilidad con la ocasión
- Interacción con la vestimenta
- Proyección en el entorno específico

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

## PERFUMES DISPONIBLES - PRIMER GRUPO
{perfumes_grupo1}

## PERFUMES DISPONIBLES - SEGUNDO GRUPO
{perfumes_grupo2}

**IMPORTANTE:** Ambos grupos deben analizarse con la misma profundidad. Ignora completamente nombres de marca. Analiza solo las características aromáticas y contextuales.

## GUÍA EXPERTA

### 🌸 PRIMAVERA
**Día:** Florales frescos, Acuáticos, Fougère, Chipre frescos
Acordes: Verde, Floral (ligero), Fresco, Acuático
**Noche:** Florales orientales, Woody florales, Ambarino suave, Gourmand ligeros
Acordes: Floral (intenso), Amaderado, Ambarino, Dulce

### ☀️ VERANO
**Día:** Cítricos, Acuáticos, Verdes, Frescos
Acordes: Cítrico, Marino, Verde, Fresco, Afrutado (ligero)
**Noche:** Florales blancos, Aromatic-fougère, Chipre modernos, Orientales frescos
Acordes: Floral blanco, Especiado (ligero), Musgo, Afrutado (tropical)

### 🍂 OTOÑO
**Día:** Chipre, Woody aromáticos, Especiados suaves, Cuero suave
Acordes: Amaderado, Musgo, Especiado, Cuero
**Noche:** Orientales ambarados, Cuero intenso, Especiados, Fougère intensos
Acordes: Ambarino, Especiado (intenso), Amaderado profundo, Resinoso

### ❄️ INVIERNO
**Día:** Orientales amaderados, Balsámicos, Gourmand sutiles, Especiados cálidos
Acordes: Amaderado, Balsámico, Especiado, Dulce
**Noche:** Orientales intensos, Cuero profundo, Gourmand ricos, Anímales
Acordes: Amaderado pesado, Oudy, Cuero, Tabacoso, Animalico, Especiado intenso

## PROCESO DE ANÁLISIS Y RECOMENDACIÓN

1. **Análisis Completo:** Evalúa TODOS los perfumes de ambos grupos considerando SOLO sus propiedades aromáticas.
2. **Análisis Ambiental:** Calcula comportamiento molecular según temperatura, humedad y espacio.
3. **Selección Preliminar:** Identifica de cada grupo los dos mejores candidatos por compatibilidad química.
4. **Evaluación Final:** Compara los 4 finalistas (2 de cada grupo) basándote ÚNICAMENTE en notas y acordes.
5. **Justificación Química:** Explica la elección basándote en datos científicos olfativos.
6. **Aplicación:** Sugiere cantidad de atomizaciones según el comportamiento molecular. **No indiques zonas del cuerpo.**

## FORMATO DE RESPUESTA

Empieza con:  
**Recomiendo usar: [NOMBRE DEL PERFUME]**

Luego estructura la respuesta con los siguientes bloques:

1. **Análisis Ambiental y Olfativo**  
2. **Evaluación de Candidatos (sin mencionar marcas)**  
   - *Finalistas del Primer Grupo por notas y acordes*
   - *Finalistas del Segundo Grupo por notas y acordes*
3. **Justificación Final (enfocada en química aromática)**  
4. **Recomendación de Aplicación**

Asegúrate de NO mencionar prestigio, popularidad o marca como criterios. Enfócate EXCLUSIVAMENTE en la compatibilidad aromática con el contexto.
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
