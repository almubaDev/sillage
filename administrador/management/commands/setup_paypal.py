from django.core.management.base import BaseCommand
from django.conf import settings
from administrador.paypal_utils import get_paypal_access_token, create_paypal_product, create_paypal_plan
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Configura productos y planes en PayPal para suscripciones"

    def handle(self, *args, **options):
        # Crear producto
        self.stdout.write("Creando producto en PayPal...")
        product_id = create_paypal_product(
            name="Sillage Premium",
            description="Suscripción mensual al recomendador de perfumes Sillage"
        )
        
        if not product_id:
            self.stdout.write(self.style.ERROR("Error al crear el producto en PayPal."))
            return
        
        self.stdout.write(self.style.SUCCESS(f"✅ Producto creado con ID: {product_id}"))
        
        # Crear plan de suscripción
        self.stdout.write("Creando plan de suscripción en PayPal...")
        plan_id = create_paypal_plan(
            product_id=product_id,
            plan_name="Sillage Premium Mensual",
            description="Suscripción mensual de $4.99 USD",
            price="4.99",
            currency="USD",
            interval="MONTH"
        )
        
        if not plan_id:
            self.stdout.write(self.style.ERROR("Error al crear el plan en PayPal."))
            return
        
        self.stdout.write(self.style.SUCCESS(f"✅ Plan creado con ID: {plan_id}"))
        
        # Indicaciones para guardar estos IDs
        self.stdout.write("\nIMPORTANTE: Guarda estos IDs en tu settings.py:")
        self.stdout.write("PAYPAL_PRODUCT_ID = '" + product_id + "'")
        self.stdout.write("PAYPAL_PLAN_ID = '" + plan_id + "'")