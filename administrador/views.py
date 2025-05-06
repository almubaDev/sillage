from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Suscripcion, HistorialPago

@login_required
def pagina_suscripcion(request):
    """Vista que muestra la página con el botón para suscribirse"""
    return render(request, 'administrador/suscripcion.html')


@login_required
def procesar_pago(request):
    """
    Vista que simula el procesamiento de un pago y redirige a la página de éxito
    En un sistema real, aquí redirigirías a la pasarela de pago externa
    """
    if request.method == 'POST':
        # Aquí normalmente generarías una redirección a la pasarela de pago
        # Para nuestra simulación, vamos directamente a la página de éxito
        return redirect('administrador:pago_exitoso')

    return redirect('administrador:pagina_suscripcion')


@login_required
def pago_exitoso(request):
    """
    Vista que se ejecuta cuando el pago es exitoso
    En un sistema real, esta vista sería llamada por la pasarela de pago
    """
    usuario = request.user

    # 1. Crear o actualizar la suscripción
    suscripcion, creada = Suscripcion.objects.get_or_create(
        usuario=usuario,
        defaults={
            'activo': True,
            'fecha_inicio': timezone.now(),
            'fecha_expiracion': timezone.now() + timezone.timedelta(days=30),
            'origen_pago': 'Test',
            'monto': 9.99,
            'moneda': 'USD',
        }
    )

    # Si la suscripción ya existía pero estaba inactiva, reactivarla
    if not creada and not suscripcion.activo:
        suscripcion.activo = True
        suscripcion.fecha_ultima_renovacion = timezone.now()
        suscripcion.fecha_expiracion = timezone.now() + timezone.timedelta(days=30)
        suscripcion.save()

    # 2. Registrar el pago en el historial
    HistorialPago.objects.create(
        usuario=usuario,
        suscripcion=suscripcion,
        monto=9.99,
        moneda='USD',
        metodo_pago='Test',
        referencia=f'TEST-{timezone.now().strftime("%Y%m%d%H%M%S")}',
        estado='completado',
        notas='Pago de prueba para suscripción mensual'
    )

    # 3. Actualizar el estado del usuario
    # (esto debería manejarse automáticamente por los signals que creamos)
    usuario.suscrito = True
    usuario.save()

    messages.success(request, '¡Suscripción activada con éxito! Se han asignado 30 consultas a tu cuenta.')

    return render(request, 'administrador/pago_exitoso.html')