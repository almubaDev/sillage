from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Suscripcion, HistorialPago
from .flow_client import FlowClient


@login_required
def pagina_suscripcion_flow(request):
    return render(request, 'administrador/suscripcion_flow.html')

#------------------------------------------------------------

@login_required
def iniciar_suscripcion_flow(request):
    """
    Inicia el proceso de suscripción con Flow.
    Si el cliente ya existe, se salta la creación y va directo al registro de tarjeta.
    """
    usuario = request.user
    flow = FlowClient()

    try:
        # Obtener o crear la suscripción (estado pendiente si no existe)
        suscripcion, creada = Suscripcion.objects.get_or_create(
            usuario=usuario,
            defaults={
                "activo": False,
                "origen_pago": "Flow",
                "monto": 4900,
                "moneda": "CLP",
                "renovacion_automatica": True
            }
        )

        # Verificar si ya tiene un flow_customer_id guardado
        if suscripcion.flow_customer_id:
            flow_customer_id = suscripcion.flow_customer_id
        else:
            # Si no existe en DB, se intenta crear en Flow
            flow_customer_id = flow.crear_cliente(
                nombre=f"{usuario.first_name} {usuario.last_name}",
                email=usuario.email,
                external_id=str(usuario.id)
            )
            # Guardar en modelo local
            suscripcion.flow_customer_id = flow_customer_id
            suscripcion.save()

        # Solicitar registro de tarjeta
        url_retorno = request.build_absolute_uri('/administrador/registro-tarjeta-completado/')
        url_flow = flow.solicitar_registro_tarjeta(customer_id=flow_customer_id, url_return=url_retorno)

        return redirect(url_flow)

    except Exception as e:
        messages.error(request, f"Error al iniciar el proceso de suscripción: {e}")
        return redirect('administrador:pagina_suscripcion_flow')







#----------------------------------------------------




@login_required
def confirmar_tarjeta_flow(request):
    token = request.GET.get('token')

    if not token:
        messages.error(request, "No se recibió el token de confirmación")
        return redirect('administrador:pagina_suscripcion_flow')

    try:
        customer_id = request.session.get('flow_customer_id')
        if not customer_id:
            messages.error(request, "Sesión expirada o inválida")
            return redirect('administrador:pagina_suscripcion_flow')

        flow_client = FlowClient()
        result = flow_client.verificar_registro_tarjeta(token)

        if result.get('status') != '1':
            messages.error(request, "Error al registrar la tarjeta")
            return redirect('administrador:pagina_suscripcion_flow')

        subscription_result = flow_client.crear_suscripcion(
            customer_id=customer_id,
            plan_id='SillageMensual'
        )

        usuario = request.user

        suscripcion, creada = Suscripcion.objects.get_or_create(
            usuario=usuario,
            defaults={
                'activo': True,
                'fecha_inicio': timezone.now(),
                'fecha_expiracion': timezone.now() + timezone.timedelta(days=30),
                'origen_pago': 'Flow',
                'monto': 4.99,
                'moneda': 'CLP',
                'referencia_pago': subscription_result['subscriptionId']
            }
        )

        if not creada:
            suscripcion.activo = True
            suscripcion.fecha_ultima_renovacion = timezone.now()
            suscripcion.fecha_expiracion = timezone.now() + timezone.timedelta(days=30)
            suscripcion.referencia_pago = subscription_result['subscriptionId']
            suscripcion.save()

        HistorialPago.objects.create(
            usuario=usuario,
            suscripcion=suscripcion,
            monto=4.99,
            moneda='CLP',
            metodo_pago='Flow',
            referencia=subscription_result['subscriptionId'],
            estado='completado',
            notas='Suscripción inicial a Sillage mediante Flow'
        )

        usuario.suscrito = True
        usuario.consultas_restantes = 30
        usuario.save()

        if 'flow_customer_id' in request.session:
            del request.session['flow_customer_id']

        messages.success(request, '¡Suscripción activada con éxito! Se han asignado 30 consultas a tu cuenta.')
        return redirect('users:perfil')

    except Exception as e:
        messages.error(request, f"Error al completar la suscripción: {str(e)}")
        return redirect('administrador:pagina_suscripcion_flow')

@login_required
def cancelar_suscripcion_flow(request):
    if request.method != 'POST':
        return redirect('users:perfil')

    try:
        usuario = request.user
        suscripcion = Suscripcion.objects.filter(usuario=usuario, activo=True).first()
        if not suscripcion:
            messages.warning(request, "No tienes una suscripción activa para cancelar.")
            return redirect('users:perfil')

        if suscripcion.origen_pago != 'Flow':
            messages.warning(request, "La suscripción no es de Flow y no puede ser cancelada automáticamente.")
            return redirect('users:perfil')

        flow_client = FlowClient()
        cancelacion_inmediata = request.POST.get('cancelacion_inmediata', '0')
        at_period_end = 0 if cancelacion_inmediata == '1' else 1

        flow_client.cancelar_suscripcion(
            subscription_id=suscripcion.referencia_pago,
            at_period_end=at_period_end
        )

        if at_period_end == 1:
            messages.success(request, "Tu suscripción ha sido programada para cancelarse al finalizar el período actual.")
        else:
            suscripcion.activo = False
            suscripcion.save()
            usuario.suscrito = False
            usuario.save()
            messages.success(request, "Tu suscripción ha sido cancelada inmediatamente.")

        return redirect('users:perfil')

    except Exception as e:
        messages.error(request, f"Error al cancelar la suscripción: {str(e)}")
        return redirect('users:perfil')

@login_required
def procesar_pago_flow(request):
    return redirect('administrador:iniciar_suscripcion_flow')

@login_required
def webhook_flow(request):
    return HttpResponse("OK")

@login_required
def pago_exitoso_flow(request):
    messages.success(request, "Operación completada con éxito.")
    return redirect('users:perfil')

@login_required
def pago_fallido_flow(request):
    messages.error(request, "La operación no pudo completarse.")
    return redirect('administrador:pagina_suscripcion_flow')
