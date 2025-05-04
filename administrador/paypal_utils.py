import requests
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)

def get_paypal_access_token():
    """Obtiene un token de acceso OAuth de PayPal"""
    auth = (settings.PAYPAL_CLIENT_ID, settings.PAYPAL_SECRET)
    data = {"grant_type": "client_credentials"}
    
    try:
        response = requests.post(
            f"{settings.PAYPAL_API_BASE}/v1/oauth2/token", 
            auth=auth, 
            data=data
        )
        response.raise_for_status()  # Verificar si la respuesta es exitosa
        return response.json().get("access_token")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al obtener token de PayPal: {e}")
        return None

def create_paypal_product(name, description="Suscripción a recomendador de perfumes"):
    """Crea un producto en PayPal"""
    token = get_paypal_access_token()
    if not token:
        return None
        
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    product_data = {
        "name": name,
        "description": description,
        "type": "SERVICE",
        "category": "SOFTWARE"
    }
    
    try:
        response = requests.post(
            f"{settings.PAYPAL_API_BASE}/v1/catalogs/products",
            json=product_data, 
            headers=headers
        )
        response.raise_for_status()
        return response.json().get("id")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al crear producto en PayPal: {e}")
        return None

def create_paypal_plan(product_id, plan_name, description, price, currency="USD", interval="MONTH"):
    """Crea un plan de suscripción en PayPal"""
    token = get_paypal_access_token()
    if not token:
        return None
        
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    plan_data = {
        "product_id": product_id,
        "name": plan_name,
        "description": description,
        "billing_cycles": [
            {
                "frequency": {"interval_unit": interval, "interval_count": 1},
                "tenure_type": "REGULAR",
                "sequence": 1,
                "total_cycles": 0,  # 0 para indefinido
                "pricing_scheme": {
                    "fixed_price": {"value": str(price), "currency_code": currency}
                }
            }
        ],
        "payment_preferences": {
            "auto_bill_outstanding": True,
            "setup_fee_failure_action": "CONTINUE",
            "payment_failure_threshold": 3
        }
    }
    
    try:
        response = requests.post(
            f"{settings.PAYPAL_API_BASE}/v1/billing/plans",
            json=plan_data, 
            headers=headers
        )
        response.raise_for_status()
        return response.json().get("id")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al crear plan en PayPal: {e}")
        return None

def get_subscription_details(subscription_id):
    """Obtiene los detalles de una suscripción desde PayPal"""
    token = get_paypal_access_token()
    if not token:
        return None
        
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(
            f"{settings.PAYPAL_API_BASE}/v1/billing/subscriptions/{subscription_id}",
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al obtener detalles de suscripción: {e}")
        return None
    
    
def cancel_paypal_subscription(subscription_id, reason="Customer requested cancellation"):
    """Cancela una suscripción en PayPal"""
    token = get_paypal_access_token()
    if not token:
        return False
        
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    payload = {
        "reason": reason
    }
    
    try:
        response = requests.post(
            f"{settings.PAYPAL_API_BASE}/v1/billing/subscriptions/{subscription_id}/cancel",
            json=payload, 
            headers=headers
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al cancelar suscripción en PayPal: {e}")
        return False