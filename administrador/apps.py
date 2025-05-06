from django.apps import AppConfig

class AdministradorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'administrador'
    
    def ready(self):
        # Importar las señales
        import administrador.signals