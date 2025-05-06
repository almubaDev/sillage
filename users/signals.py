from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import User

@receiver(pre_save, sender=User)
def actualizar_consultas_al_suscribir(sender, instance, **kwargs):
    """
    Signal que detecta cuando un usuario se suscribe y le asigna 30 consultas.
    """
    # Obtener el estado anterior del usuario (si existe)
    try:
        usuario_anterior = User.objects.get(pk=instance.pk)
        # Verificar si el usuario pasó de no suscrito a suscrito
        if not usuario_anterior.suscrito and instance.suscrito:
            # Asignar 30 consultas al usuario cuando se suscribe
            instance.consultas_restantes = 30
    except User.DoesNotExist:
        # Es un usuario nuevo, no hacemos nada
        pass