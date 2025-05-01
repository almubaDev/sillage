from django.urls import path
from .views import formulario_recomendacion

app_name = 'recomendador'

urlpatterns = [
    path('', formulario_recomendacion, name='formulario'),
]
