import requests
import csv
import time

marcas_perfumes = [
    '432',
    'acqua di parma',
    'aerin',
    'affinessence',
    'agatho',
    'akro',
    'al haramain',
    'al rehab',
    'alexandre.j',
    'almah parfums',
    'amouage',
    'amouroud',
    'andres croxatto',
    'andy tauer',
    'antiqua firenze',
    'arabian oud',
    'argos',
    'armani',
    'atelier des ors',
    'atelier materi',
    'bdk',
    'beaufort',
    'beso beach',
    'blend oud',
    'boadicea the victorious',
    'bois 1920',
    'bond no9',
    'bortnikoff',
    'botanicae',
    'bvlgari',
    'byredo',
    'byron parfums',
    'carner barcelona',
    'carolina herrera',
    'cartier',
    'casamorati',
    'chanel',
    'chopard',
    'clive christian',
    'costumatic',
    'creed',
    'croxatto',
    'd.s.& durga',
    'dali haute parfumerie',
    'daniel josier',
    'dior',
    'eight & bob',
    'elektimuss',
    'emper',
    'escentric molecules',
    'essential parfums',
    'etat libre d\'orange',
    'fragrance du bois',
    'francesca bianchi',
    'frank boclet',
    'frapin',
    'frederic malle',
    'gallagher fragrances',
    'giardini di toscana',
    'giardino benessere',
    'gisada',
    'givenchy',
    'goldfield & banks',
    'gucci',
    'guerlain',
    'histoires de parfums',
    'houbigant paris',
    'house of oud',
    'hugo boss',
    'initio',
    'jacques fath',
    'jean paul gaultier',
    'jeroboam',
    'joterc by daniel josier',
    'jovoy',
    'juliette has a gun',
    'kajal',
    'kenzo',
    'kerosene',
    'kiehl\'s',
    'kilian',
    'laboratorio olfattivo',
    'lalique',
    'les idemodables',
    'liquides imaginaires',
    'lorenzo pazzaglia',
    'louis vuitton',
    'lubin',
    'm.micallef',
    'maison crivelli',
    'maison francis kurkdjian',
    'maison label perfumes',
    'maison margiela',
    'mancera',
    'marc antoine barrois',
    'masque milano',
    'matiere premiere',
    'memo',
    'memo paris',
    'milano cento',
    'milano fragrance',
    'min new york',
    'mind games',
    'montale',
    'mood',
    'moresque',
    'morph',
    'naomi goodsir',
    'nasomatto',
    'nishane',
    'olympic orchids',
    'oman luxury',
    'ormonde jayne',
    'orto parisi',
    'paco rabanne',
    'pana dora',
    'panama 1924',
    'pantheon roma',
    'papillon',
    'parfumerie d\'aquitaine',
    'parfums de marly',
    'parfums mdci',
    'pearlescent parfums',
    'penhaligons',
    'pernoire',
    'perris monte carlo',
    'philipp plein',
    'prada',
    'primera perfumes',
    'profumo di firenze',
    'profumum roma',
    'puredistance',
    'ramon monegal',
    'rania j',
    'rasasi',
    'renier',
    'renier perfumes',
    'rirana',
    'rogue',
    'roja parfums',
    'room 1015',
    'rosendo mateu',
    'royal crown',
    'santi burgas',
    'sarah baker',
    'savoir faire',
    'scents of wood',
    'serge lutens',
    'sinergia parfums',
    'sospiro',
    'spirit of kings',
    'spiritica',
    'stephane humbert lucas',
    'tauer perfumes',
    'teo cabanel',
    'thameen',
    'thauy by daniel josier',
    'the elemental',
    'the merchant of venice',
    'the woods collection',
    'theodoros kalotinis',
    'thomas kosmala',
    'tiziana terenzi',
    'tom ford',
    'uniquee luxury',
    'v canto by tiziana terenzi',
    'valentino',
    'versace',
    'vertus',
    'viktor & rolf',
    'widian',
    'xerjoff',
    'yves saint laurent',
    'zadig & voltaire',
    'zaharoff',
    'zoologist perfumes'
]
headers = {
    "x-rapidapi-host": "fragrancefinder-api.p.rapidapi.com",
    "x-rapidapi-key": "6af27a66ebmsh24fe0d87ef0091dp1f104cjsn20ec717f6c60"  # ← Reemplaza con tu key real
}

base_url = "https://fragrancefinder-api.p.rapidapi.com/perfumes/search?q="

resultados = []

for marca in marcas_perfumes:
    try:
        print(f"Consultando: {marca}")
        response = requests.get(base_url + marca, headers=headers)
        if response.status_code == 200:
            data = response.json()
            for perfume in data:
                resultados.append({
                    "nombre": perfume.get("perfume"),
                    "marca": perfume.get("brand"),
                    "notas": ", ".join(perfume.get("notes", [])),
                    "acordes": ", ".join(perfume.get("accords", [])),
                    "descripcion": perfume.get("description"),
                    "url": perfume.get("url")
                })
        else:
            print(f"Error al consultar {marca}: {response.status_code}")
        time.sleep(1)  # delay para evitar sobrecargar la API
    except Exception as e:
        print(f"Error con {marca}: {e}")

# Guardar en CSV limpio
with open("perfumes_limpios_2.csv", "w", newline='', encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["nombre", "marca", "notas", "acordes", "descripcion", "url"])
    writer.writeheader()
    for item in resultados:
        writer.writerow(item)

print("✅ Archivo 'perfumes_limpios_2.csv' generado con éxito.")
