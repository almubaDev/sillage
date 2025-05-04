# administrador/urls.py
from django.urls import path
from . import views

app_name = 'administrador'

urlpatterns = [
    path('suscripciones/', views.lista_suscripciones, name='lista_suscripciones'),
    path('suscripciones/nueva/', views.crear_suscripcion, name='crear_suscripcion'),
    path('suscripciones/<int:pk>/editar/', views.editar_suscripcion, name='editar_suscripcion'),
    path('suscripciones/<int:pk>/eliminar/', views.eliminar_suscripcion, name='eliminar_suscripcion'),
    # Nuevas URLs para PayPal
    path('suscribirse/', views.suscripcion_view, name='suscribirse'),
    path('suscripcion/confirmar/', views.confirmar_suscripcion, name='confirmar_suscripcion'),
    path('suscripcion/cancelar/', views.cancelar_suscripcion, name='cancelar_suscripcion'),
    path('paypal-webhook/', views.paypal_webhook, name='paypal_webhook'),
]