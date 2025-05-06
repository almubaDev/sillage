from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.utils import timezone
import hashlib
import hmac
import json
import logging

from .models import Suscripcion, HistorialPago
from users.models import User

# Configurar logging
logger = logging.getLogger(__name__)

def verificar_firma_flow(datos, firma_recibida):
    """
    Verifica la autenticidad de una notificación de Flow
    """
    # Eliminar la firma de los datos para calcular la firma
    if 's' in datos:
        del datos['s']

    # Ordenar los datos alfabéticamente por clave
    datos_ordenados = sorted(datos.items())

    # Concatenar key=value con &
    cadena = '&'.join(f"{key}={value}" for key, value in datos_ordenados)

    # Firmar usando HMAC-SHA256
    firma_calculada = hmac.new(
        settings.FLOW_SECRET_KEY.encode('utf-8'),
        cadena.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    # Comparar firmas
    return firma_calculada == firma_recibida

@csrf_exempt
@require_POST
def webhook_flow_suscripcion(request):
    """
    Webhook para recibir notificaciones de Flow sobre suscripciones y pagos
    """
    try:
        # Obtener datos de la notificación
        datos = request.POST.dict()

        # Registrar la notificación recibida (para depuración)
        logger.info(f"Notificación Flow recibida: {json.dumps(datos)}")

        # Verificar la autenticidad de la notificación
        firma_recibida = datos.get('s', '')
        if not verificar_firma_flow(datos, firma_recibida):
            logger.error("Firma inválida en notificación de Flow")
            return HttpResponse("Firma inválida", status=401)

        # Obtener tipo de evento y estado
        evento = datos.get('type', '')
        status = datos.get('status', '')

        # Identificar la suscripción relacionada
        subscription_id = datos.get('subscriptionId', '')

        if not subscription_id:
            logger.error("Notificación sin ID de suscripción")
            return HttpResponse("Notificación sin ID de suscripción", status=400)

        try:
            suscripcion = Suscripcion.objects.get(referencia_pago=subscription_id)
        except Suscripcion.DoesNotExist:
            logger.error(f"Suscripción no encontrada: {subscription_id}")
            return HttpResponse("Suscripción no encontrada", status=404)

        # Procesar según el tipo de evento
        if evento == 'subscription_payment' and status == '2':  # Pago de suscripción exitoso
            # Actualizar fechas de la suscripción
            suscripcion.activo = True
            suscripcion.fecha_ultima_renovacion = timezone.now()

            # Calcular nueva fecha de expiración (30 días desde hoy)
            suscripcion.fecha_expiracion = timezone.now() + timezone.timedelta(days=30)
            suscripcion.save()

            # Registrar el pago en el historial
            HistorialPago.objects.create(
                usuario=suscripcion.usuario,
                suscripcion=suscripcion,
                monto=suscripcion.monto,
                moneda=suscripcion.moneda,
                metodo_pago='Flow',
                referencia=datos.get('flowOrder', ''),
                estado='completado',
                notas=f"Renovación automática de suscripción"
            )

            # Actualizar consultas del usuario
            usuario = suscripcion.usuario
            usuario.consultas_restantes = 30  # Asignar 30 consultas mensuales
            usuario.suscrito = True
            usuario.save()

            logger.info(f"Renovación exitosa para suscripción {subscription_id}")

        elif evento == 'subscription_payment' and status != '2':  # Pago fallido
            # Registrar el intento fallido
            HistorialPago.objects.create(
                usuario=suscripcion.usuario,
                suscripcion=suscripcion,
                monto=suscripcion.monto,
                moneda=suscripcion.moneda,
                metodo_pago='Flow',
                referencia=datos.get('flowOrder', ''),
                estado='fallido',
                notas=f"Intento fallido de cobro. Estado: {status}"
            )

            logger.warning(f"Pago fallido para suscripción {subscription_id}")

        elif evento == 'subscription_canceled':  # Suscripción cancelada
            # Marcar como inactiva
            suscripcion.activo = False
            suscripcion.save()

            # Actualizar usuario
            usuario = suscripcion.usuario
            usuario.suscrito = False
            usuario.save()

            logger.info(f"Suscripción cancelada: {subscription_id}")

        elif evento == 'subscription_status_changed':  # Cambio de estado
            # Actualizar estado según la notificación
            nuevo_estado = datos.get('new_status', '')
            if nuevo_estado == '0':  # Inactiva
                suscripcion.activo = False
                suscripcion.save()

                usuario = suscripcion.usuario
                usuario.suscrito = False
                usuario.save()

                logger.info(f"Suscripción desactivada: {subscription_id}")
            elif nuevo_estado == '1':  # Activa
                suscripcion.activo = True
                suscripcion.save()

                usuario = suscripcion.usuario
                usuario.suscrito = True
                usuario.save()

                logger.info(f"Suscripción activada: {subscription_id}")

        # Responder OK para todas las notificaciones procesadas correctamente
        return HttpResponse("OK", status=200)

    except Exception as e:
        logger.error(f"Error procesando webhook Flow: {str(e)}")
        # Siempre devolver 200 para que Flow no reintente
        return HttpResponse("Error procesando notificación", status=200)