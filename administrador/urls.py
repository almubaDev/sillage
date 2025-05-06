# En administrador/urls.py
from django.urls import path
from . import views, views_flow, views_flow_webhook
app_name = 'administrador'
urlpatterns = [
    # Test
    path('suscribirse/', views.pagina_suscripcion, name='pagina_suscripcion'),
    path('procesar-pago/', views.procesar_pago, name='procesar_pago'),
    path('pago-exitoso/', views.pago_exitoso, name='pago_exitoso'),
    
    # Flow (suscripciones recurrentes)
    path('suscribirse-flow/', views_flow.pagina_suscripcion_flow, name='pagina_suscripcion_flow'),
    path('iniciar-suscripcion-flow/', views_flow.iniciar_suscripcion_flow, name='iniciar_suscripcion_flow'),
    path('confirmar-tarjeta-flow/', views_flow.confirmar_tarjeta_flow, name='confirmar_tarjeta_flow'),
    path('cancelar-suscripcion-flow/', views_flow.cancelar_suscripcion_flow, name='cancelar_suscripcion_flow'),
    
    # Webhook para Flow Suscripciones
    path('webhook-flow-suscripcion/', views_flow_webhook.webhook_flow_suscripcion, name='webhook_flow_suscripcion'),
]