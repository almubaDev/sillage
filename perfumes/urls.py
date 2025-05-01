from django.urls import path
from .views import mis_perfumes, eliminar_perfume

app_name = 'perfumes'

urlpatterns = [
    path('', mis_perfumes, name='mis_perfumes'),
    path('eliminar/<int:pk>/', eliminar_perfume, name='eliminar_perfume'),
]