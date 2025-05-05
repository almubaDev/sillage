from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import gettext_lazy as _

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  # para cambiar el idioma desde la app
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('usuarios/', include('users.urls', namespace='users')),
    path('perfumes/', include('perfumes.urls', namespace='perfumes')),
    path('recomendador/', include('recomendador.urls', namespace='recomendador')),
    #path('administrador/', include('administrador.urls', namespace='administrador')),
    path('', include('home.urls', namespace='home')),

    prefix_default_language=True,  # Asegura prefijo de idioma siempre presente
)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)