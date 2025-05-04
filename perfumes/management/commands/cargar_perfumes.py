import csv
import ast
from django.core.management.base import BaseCommand
from perfumes.models import Perfume

class Command(BaseCommand):
    help = "Importa perfumes desde un CSV limpio. Usa --reset para eliminar todos los perfumes antes."

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Ruta al archivo perfumes_limpios.csv")
        parser.add_argument("--reset", action="store_true", help="Eliminar todos los perfumes antes de importar")

    def limpiar_lista(self, cadena):
        try:
            valor = ast.literal_eval(cadena)
            if isinstance(valor, list):
                return valor
            elif isinstance(valor, str):
                return [valor]
            else:
                return []
        except Exception:
            if "," in cadena:
                return [x.strip() for x in cadena.split(",")]
            return [cadena.strip()]

    def handle(self, *args, **options):
        ruta_csv = options["csv_file"]
        reset = options["reset"]

        if reset:
            confirm = input("⚠️ ¿Seguro que quieres eliminar todos los perfumes existentes? (s/n): ")
            if confirm.lower() == "s":
                Perfume.objects.all().delete()
                self.stdout.write(self.style.WARNING("Todos los perfumes han sido eliminados."))
            else:
                self.stdout.write(self.style.NOTICE("Cancelado. No se eliminó nada."))
                return

        total = 0
        ya_existia = 0

        with open(ruta_csv, newline='', encoding="utf-8") as archivo:
            reader = csv.DictReader(archivo)

            for fila in reader:
                nombre = fila["Perfume"].strip()
                marca = fila["Brand"].strip()
                perfumista = fila.get("Perfumer1", "").strip()
                notas = self.limpiar_lista(fila.get("Notas", ""))
                acordes = self.limpiar_lista(fila.get("Acordes", ""))

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
            self.stdout.write(self.style.WARNING(f"⚠️ {ya_existia} perfumes ya existían y no se duplicaron."))
            
            
# manage.py cargar_perfumes /home/almubadev/sillage/perfumes_db2.csv --reset
