from django.urls import path
from . import views, views_flow, views_flow_webhook

app_name = 'administrador'

urlpatterns = [
    # Test
    path('suscribirse/', views.pagina_suscripcion, name='pagina_suscripcion'),
    path('procesar-pago/', views.procesar_pago, name='procesar_pago'),
    path('pago-exitoso/', views.pago_exitoso, name='pago_exitoso'),
    
    # Flow (sistema existente)
    path('suscribirse-flow/', views_flow.pagina_suscripcion_flow, name='pagina_suscripcion_flow'),
    path('procesar-pago-flow/', views_flow.procesar_pago_flow, name='procesar_pago_flow'),
    path('webhook-flow/', views_flow.webhook_flow, name='webhook_flow'),
    path('pago-exitoso-flow/', views_flow.pago_exitoso_flow, name='pago_exitoso_flow'),
    path('pago-fallido-flow/', views_flow.pago_fallido_flow, name='pago_fallido_flow'),
    
    # Flow (suscripciones recurrentes)
    path('iniciar-suscripcion-flow/', views_flow.iniciar_suscripcion_flow, name='iniciar_suscripcion_flow'),
    path('confirmar-tarjeta-flow/', views_flow.confirmar_tarjeta_flow, name='confirmar_tarjeta_flow'),
    path('cancelar-suscripcion-flow/', views_flow.cancelar_suscripcion_flow, name='cancelar_suscripcion_flow'),
    
    # Webhook para Flow Suscripciones
    path('webhook-flow-suscripcion/', views_flow_webhook.webhook_flow_suscripcion, name='webhook_flow_suscripcion'),
]