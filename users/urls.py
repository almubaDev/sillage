from django.urls import path
from .views import CustomLoginView, CustomLogoutView, RegisterView, perfil_view

app_name = 'users'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('registro/', RegisterView.as_view(), name='register'),
    path('perfil/', perfil_view, name='perfil'),  
]
