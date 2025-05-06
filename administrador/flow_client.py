import hashlib
import hmac
import time
import requests
from django.conf import settings

class FlowClient:
    """Cliente básico para interactuar con la API de Flow"""
    
    def __init__(self):
        self.api_key = settings.FLOW_API_KEY
        self.secret_key = settings.FLOW_SECRET_KEY
        self.api_url = settings.FLOW_API_URL
    
    def crear_firma(self, datos):
        """
        Crea una firma para autenticar peticiones a Flow
        
        Args:
            datos: Diccionario con los parámetros a firmar
        
        Returns:
            Firma generada con HMAC-SHA256
        """
        # Ordenar los datos alfabéticamente por clave
        datos_ordenados = sorted(datos.items())
        
        # Concatenar key=value con &
        cadena = '&'.join(f"{key}={value}" for key, value in datos_ordenados)
        
        # Firmar usando HMAC-SHA256
        firma = hmac.new(
            self.secret_key.encode('utf-8'),
            cadena.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return firma
    
    def crear_orden(self, monto, concepto, email, orden_id=None, url_confirmacion=None, url_exito=None, url_fracaso=None):
        """
        Crea una orden de pago en Flow
        
        Args:
            monto: Monto a cobrar (ejemplo: 4990 para $4.990)
            concepto: Descripción del cobro
            email: Email del usuario
            orden_id: ID opcional para la orden
            url_confirmacion: URL donde Flow enviará la confirmación
            url_exito: URL donde redirigir al usuario tras pago exitoso
            url_fracaso: URL donde redirigir al usuario si el pago falla
            
        Returns:
            URL de pago a la que redirigir al usuario
        """
        # Generar un ID de orden si no se proporciona uno
        if not orden_id:
            orden_id = f"ORD-{email.split('@')[0]}-{int(time.time())}"
        
        # Usar URLs proporcionadas o valores predeterminados
        if not url_confirmacion:
            url_confirmacion = "https://tudominio.cl/administrador/webhook-flow/"
        if not url_exito:
            url_exito = "https://tudominio.cl/administrador/pago-exitoso-flow/"
        if not url_fracaso:
            url_fracaso = "https://tudominio.cl/administrador/pago-fallido-flow/"
        
        # Datos del pago
        datos = {
            "apiKey": self.api_key,
            "amount": str(monto),
            "commerceOrder": orden_id,
            "currency": "CLP",
            "email": email,
            "subject": concepto,
            "urlConfirmation": url_confirmacion,
            "urlReturn": url_exito,
            "urlCancel": url_fracaso,
        }
        
        # Añadir firma
        datos["s"] = self.crear_firma(datos)
        
        # Llamar a la API de Flow
        endpoint = "/payment/create"
        url = f"{self.api_url}{endpoint}"
        
        response = requests.post(url, data=datos)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 200:
                return data.get("url") + "?token=" + data.get("token")
            else:
                raise Exception(f"Error de Flow: {data.get('message')}")
        
        # En caso de error
        raise Exception(f"Error al crear orden de pago: {response.text}")
    
    def verificar_pago(self, token):
        """
        Verifica el estado de un pago
        
        Args:
            token: Token del pago
            
        Returns:
            Datos del pago si es exitoso
        """
        datos = {
            "apiKey": self.api_key,
            "token": token
        }
        
        # Añadir firma
        datos["s"] = self.crear_firma(datos)
        
        # Llamar a la API de Flow
        endpoint = "/payment/getStatus"
        url = f"{self.api_url}{endpoint}"
        
        response = requests.post(url, data=datos)
        
        if response.status_code == 200:
            return response.json()
        
        # En caso de error
        raise Exception(f"Error al verificar pago: {response.text}")
    
    # --- Nuevos métodos para suscripciones recurrentes ---
    
    def crear_cliente(self, nombre, email, external_id):
        """
        Registra un nuevo cliente en Flow
        
        Args:
            nombre: Nombre completo del cliente
            email: Email del cliente
            external_id: ID en nuestro sistema
            
        Returns:
            customerId: ID del cliente en Flow
        """
        datos = {
            "apiKey": self.api_key,
            "name": nombre,
            "email": email,
            "externalId": external_id
        }
        
        # Añadir firma
        datos["s"] = self.crear_firma(datos)
        
        # Llamar a la API de Flow
        endpoint = "/customer/create"
        url = f"{self.api_url}{endpoint}"
        
        response = requests.post(url, data=datos)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("customerId")
        else:
            raise Exception(f"Error al crear cliente: {response.text}")
    
    def solicitar_registro_tarjeta(self, customer_id, url_return):
        """
        Solicita al cliente registrar su tarjeta para pagos recurrentes
        
        Args:
            customer_id: ID del cliente en Flow
            url_return: URL donde Flow redirigirá después del registro
            
        Returns:
            URL de redirección para que el cliente registre su tarjeta
        """
        datos = {
            "apiKey": self.api_key,
            "customerId": customer_id,
            "url_return": url_return
        }
        
        # Añadir firma
        datos["s"] = self.crear_firma(datos)
        
        # Llamar a la API de Flow
        endpoint = "/customer/register"
        url = f"{self.api_url}{endpoint}"
        
        response = requests.post(url, data=datos)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("url") + "?token=" + data.get("token")
        else:
            raise Exception(f"Error al solicitar registro de tarjeta: {response.text}")
    
    def verificar_registro_tarjeta(self, token):
        """
        Verifica el estado del registro de tarjeta
        
        Args:
            token: Token enviado por Flow
            
        Returns:
            Datos del registro
        """
        datos = {
            "apiKey": self.api_key,
            "token": token
        }
        
        # Añadir firma
        datos["s"] = self.crear_firma(datos)
        
        # Llamar a la API de Flow
        endpoint = "/customer/getRegisterStatus"
        url = f"{self.api_url}{endpoint}"
        
        response = requests.get(url, params=datos)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error al verificar registro: {response.text}")
    
    def crear_suscripcion(self, customer_id, plan_id):
        """
        Crea una suscripción para un cliente
        
        Args:
            customer_id: ID del cliente en Flow
            plan_id: ID del plan en Flow
            
        Returns:
            Datos de la suscripción creada
        """
        datos = {
            "apiKey": self.api_key,
            "customerId": customer_id,
            "planId": plan_id
        }
        
        # Añadir firma
        datos["s"] = self.crear_firma(datos)
        
        # Llamar a la API de Flow
        endpoint = "/subscription/create"
        url = f"{self.api_url}{endpoint}"
        
        response = requests.post(url, data=datos)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error al crear suscripción: {response.text}")
    
    def obtener_suscripcion(self, subscription_id):
        """
        Obtiene datos de una suscripción
        
        Args:
            subscription_id: ID de la suscripción en Flow
            
        Returns:
            Datos de la suscripción
        """
        datos = {
            "apiKey": self.api_key,
            "subscriptionId": subscription_id
        }
        
        # Añadir firma
        datos["s"] = self.crear_firma(datos)
        
        # Llamar a la API de Flow
        endpoint = "/subscription/get"
        url = f"{self.api_url}{endpoint}"
        
        response = requests.get(url, params=datos)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error al obtener suscripción: {response.text}")
    
    def cancelar_suscripcion(self, subscription_id, at_period_end=0):
        """
        Cancela una suscripción
        
        Args:
            subscription_id: ID de la suscripción en Flow
            at_period_end: 0 para cancelar inmediatamente, 1 para cancelar al finalizar período
            
        Returns:
            Datos de la suscripción actualizada
        """
        datos = {
            "apiKey": self.api_key,
            "subscriptionId": subscription_id,
            "at_period_end": at_period_end
        }
        
        # Añadir firma
        datos["s"] = self.crear_firma(datos)
        
        # Llamar a la API de Flow
        endpoint = "/subscription/cancel"
        url = f"{self.api_url}{endpoint}"
        
        response = requests.post(url, data=datos)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error al cancelar suscripción: {response.text}")