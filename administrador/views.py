from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
import json
import logging
from .models import Suscripcion
from .forms import SuscripcionForm
from .paypal_utils import get_subscription_details, cancel_paypal_subscription
from django.utils import timezone
from datetime import timedelta

# Configurar logging
logger = logging.getLogger(__name__)

# Vistas originales
@login_required
def lista_suscripciones(request):
    suscripciones = Suscripcion.objects.filter(usuario=request.user)
    return render(request, 'administrador/lista_suscripciones.html', {'suscripciones': suscripciones})

@login_required
def crear_suscripcion(request):
    if request.method == 'POST':
        form = SuscripcionForm(request.POST)
        if form.is_valid():
            nueva = form.save(commit=False)
            nueva.usuario = request.user
            nueva.save()
            return redirect('administrador:lista_suscripciones')
    else:
        form = SuscripcionForm()
    return render(request, 'administrador/formulario_suscripcion.html', {'form': form})

@login_required
def editar_suscripcion(request, pk):
    suscripcion = get_object_or_404(Suscripcion, pk=pk, usuario=request.user)
    if request.method == 'POST':
        form = SuscripcionForm(request.POST, instance=suscripcion)
        if form.is_valid():
            form.save()
            return redirect('administrador:lista_suscripciones')
    else:
        form = SuscripcionForm(instance=suscripcion)
    return render(request, 'administrador/formulario_suscripcion.html', {'form': form})

@login_required
def eliminar_suscripcion(request, pk):
    suscripcion = get_object_or_404(Suscripcion, pk=pk, usuario=request.user)
    if request.method == 'POST':
        suscripcion.delete()
        return redirect('administrador:lista_suscripciones')
    return render(request, 'administrador/confirmar_eliminar.html', {'suscripcion': suscripcion})

# Nuevas vistas para PayPal
@login_required
def suscripcion_view(request):
    # Debug logs
    logger.info("PayPal Integration - Loading subscription view")
    logger.info(f"PayPal Client ID: {settings.PAYPAL_CLIENT_ID[:10]}... (truncated)")
    logger.info(f"PayPal Plan ID: {settings.PAYPAL_PLAN_ID}")
    
    # Print to console for immediate debug
    print("DEBUG - PayPal Integration")
    print(f"Client ID: {settings.PAYPAL_CLIENT_ID[:10]}... (truncated)")
    print(f"Plan ID: {settings.PAYPAL_PLAN_ID}")
    print(f"Client ID length: {len(settings.PAYPAL_CLIENT_ID)}")
    
    # Verificar si estamos regresando con un ID de suscripción
    subscription_id = request.GET.get('subscription_id')
    if subscription_id:
        logger.info(f"Returning from PayPal with subscription ID: {subscription_id}")
    
    context = {
        'client_id': settings.PAYPAL_CLIENT_ID,
        'plan_id': settings.PAYPAL_PLAN_ID,
        'precio_mensual': '4.99',
        'moneda': 'USD',
        'debug_mode': settings.DEBUG
    }
    
    # Verify context for debugging
    print(f"Context client_id length: {len(context['client_id'])}")
    
    return render(request, 'administrador/suscripcion.html', context)

@csrf_exempt
@login_required
def confirmar_suscripcion(request):
    logger.info("PayPal Integration - Confirming subscription")
    
    if request.method != 'POST':
        logger.warning("Invalid method for subscription confirmation")
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        subscription_id = data.get('subscriptionID')
        
        logger.info(f"Received subscription ID: {subscription_id}")
        
        if not subscription_id:
            logger.warning("No subscription ID provided")
            return JsonResponse({'error': 'ID de suscripción no proporcionado'}, status=400)
        
        # Obtener detalles de la suscripción desde PayPal
        logger.info("Fetching subscription details from PayPal")
        subscription_details = get_subscription_details(subscription_id)
        
        if not subscription_details:
            logger.error("Could not retrieve subscription details from PayPal")
            return JsonResponse({'error': 'No se pudieron obtener detalles de la suscripción'}, status=400)
        
        logger.info(f"Subscription details retrieved: Plan ID = {subscription_details.get('plan_id')}")
        
        # Verificar si ya existe una suscripción para este usuario
        try:
            suscripcion = Suscripcion.objects.get(usuario=request.user)
            logger.info(f"Updating existing subscription for user {request.user.email}")
            
            suscripcion.activo = True
            suscripcion.tipo = Suscripcion.TipoSuscripcion.MENSUAL
            suscripcion.origen_pago = Suscripcion.OrigenPago.PAYPAL
            suscripcion.fecha_inicio = timezone.now()
            
            # Si la suscripción ya existía, actualizamos sus valores
            suscripcion.paypal_subscription_id = subscription_id
            suscripcion.paypal_plan_id = subscription_details.get('plan_id')
            suscripcion.renovacion_automatica = True
            
            # Establecer fecha de expiración aproximada (1 mes desde ahora)
            suscripcion.fecha_expiracion = timezone.now() + timedelta(days=30)
            
            # Consultas por defecto para plan mensual
            suscripcion.consultas_restantes = 30
            
            suscripcion.save()
            logger.info("Existing subscription updated successfully")
            
        except Suscripcion.DoesNotExist:
            # Crear nueva suscripción
            logger.info(f"Creating new subscription for user {request.user.email}")
            suscripcion = Suscripcion.objects.create(
                usuario=request.user,
                tipo=Suscripcion.TipoSuscripcion.MENSUAL,
                activo=True,
                origen_pago=Suscripcion.OrigenPago.PAYPAL,
                paypal_subscription_id=subscription_id,
                paypal_plan_id=subscription_details.get('plan_id'),
                renovacion_automatica=True,
                consultas_restantes=30,
                fecha_expiracion=timezone.now() + timedelta(days=30)
            )
            logger.info("New subscription created successfully")
        
        return JsonResponse({
            'success': True,
            'message': 'Suscripción activada correctamente',
            'subscription_id': subscription_id
        })
        
    except Exception as e:
        logger.error(f"Error during subscription confirmation: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def cancelar_suscripcion(request):
    logger.info(f"PayPal Integration - Cancellation request for user {request.user.email}")
    
    if request.method != 'POST':
        logger.warning("Invalid method for subscription cancellation")
        return redirect('users:perfil')
    
    try:
        suscripcion = get_object_or_404(Suscripcion, usuario=request.user)
        
        if suscripcion.paypal_subscription_id:
            # Cancelar en PayPal
            logger.info(f"Attempting to cancel PayPal subscription: {suscripcion.paypal_subscription_id}")
            cancelado = cancel_paypal_subscription(suscripcion.paypal_subscription_id)
            
            if cancelado:
                # Actualizar en la base de datos
                suscripcion.activo = False
                suscripcion.renovacion_automatica = False
                suscripcion.save()
                
                logger.info("Subscription cancelled successfully in PayPal and database")
                messages.success(request, _("Tu suscripción ha sido cancelada correctamente."))
            else:
                logger.error("Failed to cancel subscription in PayPal")
                messages.error(request, _("No se pudo cancelar la suscripción en PayPal."))
        else:
            # Para suscripciones sin PayPal
            logger.info("Cancelling non-PayPal subscription")
            suscripcion.activo = False
            suscripcion.renovacion_automatica = False
            suscripcion.save()
            
            logger.info("Subscription marked as inactive in database")
            messages.success(request, _("Tu suscripción ha sido cancelada correctamente."))
            
    except Suscripcion.DoesNotExist:
        logger.warning(f"No active subscription found for user {request.user.email}")
        messages.error(request, _("No tienes una suscripción activa."))
    
    return redirect('users:perfil')

@csrf_exempt
def paypal_webhook(request):
    """
    Recibe y procesa webhooks de PayPal para suscripciones
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    # Para debug en desarrollo
    logger.info("PayPal Webhook recibido")
    logger.info(f"Headers: {request.headers}")
    
    try:
        event_data = json.loads(request.body)
        event_type = event_data.get('event_type')
        
        logger.info(f"Evento PayPal recibido: {event_type}")
        logger.info(f"Datos del evento: {event_data}")
        
        # Procesar diferentes tipos de eventos
        if event_type == 'BILLING.SUBSCRIPTION.CREATED':
            # Extraer ID de suscripción
            subscription_id = event_data.get('resource', {}).get('id')
            
            if subscription_id:
                logger.info(f"Nueva suscripción creada: {subscription_id}")
                # Aquí puedes implementar lógica para confirmar la suscripción
                # Similar a lo que haces en confirmar_suscripcion
            
        # Puedes añadir más manejadores de eventos aquí
        
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        logger.error(f"Error procesando webhook de PayPal: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)