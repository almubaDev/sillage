import csv
import ast
from django.core.management.base import BaseCommand
from perfumes.models import Perfume

class Command(BaseCommand):
    help = "Importa perfumes desde un CSV limpio a la base de datos"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Ruta al archivo perfumes_limpios.csv")

    def handle(self, *args, **options):
        ruta_csv = options["csv_file"]
        total = 0
        ya_existia = 0

        with open(ruta_csv, newline='', encoding="utf-8") as archivo:
            reader = csv.DictReader(archivo)

            for fila in reader:
                nombre = fila["Perfume"].strip()
                marca = fila["Brand"].strip()
                perfumista = fila.get("Perfumer1", "").strip()
                try:
                    notas = ast.literal_eval(fila["Notas"])
                    acordes = ast.literal_eval(fila["Acordes"])
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Error al convertir notas/acordes: {e}"))
                    continue

                # Evitar duplicados
                if Perfume.objects.filter(nombre=nombre, marca=marca).exists():
                    ya_existia += 1
                    continue

                Perfume.objects.create(
                    nombre=nombre,
                    marca=marca,
                    perfumista=perfumista if perfumista else None,
                    notas=notas,
                    acordes=acordes,
                )
                total += 1

        self.stdout.write(self.style.SUCCESS(f"✅ {total} perfumes importados correctamente."))
        if ya_existia:
            self.stdout.write(self.style.WARNING(f"⚠️ {ya_existia} perfumes ya existían."))
