from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site

from .models import Suscripcion, HistorialPago
from .flow_client import FlowClient

@login_required
def pagina_suscripcion_flow(request):
    """Vista que muestra la página de suscripción con Flow"""
    return render(request, 'administrador/suscripcion_flow.html')

@login_required
def iniciar_suscripcion_flow(request):
    """
    Inicia el proceso de suscripción con Flow
    1. Registra al usuario como cliente en Flow
    2. Redirige al usuario para registrar su tarjeta
    """
    if request.method != 'POST':
        return redirect('administrador:pagina_suscripcion_flow')
    
    try:
        usuario = request.user
        
        # Verificar si ya tiene una suscripción activa
        suscripcion_existente = Suscripcion.objects.filter(usuario=usuario, activo=True).first()
        if suscripcion_existente:
            messages.info(request, "Ya tienes una suscripción activa.")
            return redirect('users:perfil')
        
        # Instanciar el cliente de Flow
        flow_client = FlowClient()
        
        # 1. Registrar al usuario como cliente en Flow
        nombre_completo = f"{usuario.first_name} {usuario.last_name}".strip()
        if not nombre_completo:
            nombre_completo = f"Usuario {usuario.id}"
        
        customer_id = flow_client.crear_cliente(
            nombre=nombre_completo,
            email=usuario.email,
            external_id=str(usuario.id)
        )
        
        # 2. Construir URL de retorno
        current_site = get_current_site(request)
        domain = current_site.domain
        protocol = 'https' if request.is_secure() else 'http'
        url_return = f"{protocol}://{domain}{reverse('administrador:confirmar_tarjeta_flow')}"
        
        # 3. Redirigir al usuario para registrar su tarjeta
        redirect_url = flow_client.solicitar_registro_tarjeta(
            customer_id=customer_id,
            url_return=url_return
        )
        
        # Guardar temporalmente el customer_id en la sesión
        request.session['flow_customer_id'] = customer_id
        
        # Redirigir al usuario a Flow para registrar su tarjeta
        return redirect(redirect_url)
        
    except Exception as e:
        messages.error(request, f"Error al iniciar el proceso de suscripción: {str(e)}")
        return redirect('administrador:pagina_suscripcion_flow')

@login_required
def confirmar_tarjeta_flow(request):
    """
    Maneja la redirección de Flow después de que el usuario registra su tarjeta
    1. Verifica el registro de la tarjeta
    2. Crea la suscripción en Flow
    3. Actualiza los registros locales
    """
    # Obtener el token de la URL
    token = request.GET.get('token')
    
    if not token:
        messages.error(request, "No se recibió el token de confirmación")
        return redirect('administrador:pagina_suscripcion_flow')
    
    try:
        # Recuperar el customer_id de la sesión
        customer_id = request.session.get('flow_customer_id')
        if not customer_id:
            messages.error(request, "Sesión expirada o inválida")
            return redirect('administrador:pagina_suscripcion_flow')
        
        # Instanciar el cliente de Flow
        flow_client = FlowClient()
        
        # 1. Verificar el registro de la tarjeta
        result = flow_client.verificar_registro_tarjeta(token)
        
        if result.get('status') != '1':
            messages.error(request, "Error al registrar la tarjeta")
            return redirect('administrador:pagina_suscripcion_flow')
        
        # 2. Crear la suscripción en Flow
        subscription_result = flow_client.crear_suscripcion(
            customer_id=customer_id,
            plan_id='SillageMensual'  # ID del plan creado en Flow
        )
        
        # 3. Actualizar registros locales
        usuario = request.user
        
        # Crear o actualizar la suscripción en nuestra base de datos
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
        
        # Registrar el pago inicial en el historial
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
        
        # Actualizar usuario
        usuario.suscrito = True
        usuario.consultas_restantes = 30  # Asignar 30 consultas iniciales
        usuario.save()
        
        # Limpiar la sesión
        if 'flow_customer_id' in request.session:
            del request.session['flow_customer_id']
        
        messages.success(request, '¡Suscripción activada con éxito! Se han asignado 30 consultas a tu cuenta.')
        return redirect('users:perfil')
        
    except Exception as e:
        messages.error(request, f"Error al completar la suscripción: {str(e)}")
        return redirect('administrador:pagina_suscripcion_flow')

@login_required
def cancelar_suscripcion_flow(request):
    """
    Permite al usuario cancelar su suscripción recurrente en Flow
    """
    if request.method != 'POST':
        return redirect('users:perfil')
    
    try:
        usuario = request.user
        
        # Verificar si tiene una suscripción activa
        suscripcion = Suscripcion.objects.filter(usuario=usuario, activo=True).first()
        if not suscripcion:
            messages.warning(request, "No tienes una suscripción activa para cancelar.")
            return redirect('users:perfil')
        
        # Verificar que la suscripción sea de Flow
        if suscripcion.origen_pago != 'Flow':
            messages.warning(request, "La suscripción no es de Flow y no puede ser cancelada automáticamente.")
            return redirect('users:perfil')
        
        # Instanciar el cliente de Flow
        flow_client = FlowClient()
        
        # Cancelar la suscripción en Flow
        # at_period_end=1 para cancelar al finalizar el período vigente
        # at_period_end=0 para cancelar inmediatamente
        cancelacion_inmediata = request.POST.get('cancelacion_inmediata', '0')
        at_period_end = 0 if cancelacion_inmediata == '1' else 1
        
        flow_client.cancelar_suscripcion(
            subscription_id=suscripcion.referencia_pago,
            at_period_end=at_period_end
        )
        
        if at_period_end == 1:
            # La suscripción se cancelará al finalizar el período
            messages.success(request, "Tu suscripción ha sido programada para cancelarse al finalizar el período actual. Podrás seguir disfrutando de los beneficios hasta entonces.")
        else:
            # Cancelación inmediata
            suscripcion.activo = False
            suscripcion.save()
            
            usuario.suscrito = False
            usuario.save()
            
            messages.success(request, "Tu suscripción ha sido cancelada inmediatamente.")
        
        return redirect('users:perfil')
        
    except Exception as e:
        messages.error(request, f"Error al cancelar la suscripción: {str(e)}")
        return redirect('users:perfil')