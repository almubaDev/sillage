from django.urls import path
from . import views
app_name = 'perfumes'

urlpatterns = [
    path("", views.mi_coleccion, name="mi_coleccion"),
    path("buscar/", views.buscar_perfumes, name="buscar_perfumes"),
    path("agregar/<int:perfume_id>/", views.agregar_a_coleccion, name="agregar_perfume"),
    path("eliminar/<int:perfume_id>/", views.eliminar_de_coleccion, name="eliminar_perfume"),
    path("nuevo/", views.nuevo_perfume, name="nuevo_perfume"),
    
]