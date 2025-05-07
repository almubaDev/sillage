import hashlib
import hmac
import subprocess
import json
from django.conf import settings


class FlowClient:
    """Cliente robusto para Flow usando subprocess + curl para evitar errores con requests"""

    def __init__(self):
        self.api_key = settings.FLOW_API_KEY
        self.secret_key = settings.FLOW_SECRET_KEY
        self.api_url = settings.FLOW_API_URL

    def crear_firma(self, datos):
        datos_ordenados = sorted(datos.items())
        cadena = '&'.join(f"{key}={value}" for key, value in datos_ordenados)
        return hmac.new(
            self.secret_key.encode('utf-8'),
            cadena.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def crear_cliente(self, nombre, email, external_id):
        datos = {
            "apiKey": self.api_key,
            "name": nombre.strip(),
            "email": email.strip(),
            "externalId": str(external_id).strip()
        }
        datos["s"] = self.crear_firma(datos)

        curl_command = [
            "curl", "-s", "-L", "-X", "POST", f"{self.api_url}/customer/create"
        ] + sum([["-d", f"{k}={v}"] for k, v in datos.items()], [])

        result = subprocess.run(curl_command, capture_output=True, text=True)

        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            raise Exception(f"Respuesta inválida de Flow: {result.stdout}")

        if "customerId" in data:
            return data["customerId"]
        else:
            raise Exception(f"Error al crear cliente: {data}")

    def solicitar_registro_tarjeta(self, customer_id, url_return):
        datos = {
            "apiKey": self.api_key,
            "customerId": customer_id.strip(),
            "url_return": url_return.strip()
        }
        datos["s"] = self.crear_firma(datos)

        curl_command = [
            "curl", "-s", "-L", "-X", "POST", f"{self.api_url}/customer/register"
        ] + sum([["-d", f"{k}={v}"] for k, v in datos.items()], [])

        result = subprocess.run(curl_command, capture_output=True, text=True)

        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            raise Exception(f"Respuesta inválida de Flow: {result.stdout}")

        if "url" in data and "token" in data:
            return data["url"] + "?token=" + data["token"]
        else:
            raise Exception(f"Error al registrar tarjeta: {data}")

    def verificar_registro_tarjeta(self, token):
        datos = {
            "apiKey": self.api_key,
            "token": token.strip()
        }
        datos["s"] = self.crear_firma(datos)

        curl_command = [
            "curl", "-s", "-L", "-G", f"{self.api_url}/customer/getRegisterStatus",
            "--data-urlencode", f"apiKey={datos['apiKey']}",
            "--data-urlencode", f"token={datos['token']}",
            "--data-urlencode", f"s={datos['s']}"
        ]

        result = subprocess.run(curl_command, capture_output=True, text=True)

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            raise Exception(f"Error al verificar registro: {result.stdout}")
