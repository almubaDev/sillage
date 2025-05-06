from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings
from users.models import User
from .models import Suscripcion

# Variable para evitar recursión infinita
procesando_signal = False

@receiver(pre_save, sender=User)
def sincronizar_usuario_a_suscripcion(sender, instance, **kwargs):
    """
    Signal que se activa cuando se guarda un usuario.
    Detecta cambios en el campo 'suscrito' y actualiza la suscripción correspondiente.
    """
    global procesando_signal
    
    # Evitar recursión infinita
    if procesando_signal:
        return
    
    try:
        # Verificar si es un usuario existente
        if instance.pk:
            usuario_anterior = User.objects.get(pk=instance.pk)
            
            # Detectar si el campo 'suscrito' cambió a True
            if instance.suscrito and not usuario_anterior.suscrito:
                procesando_signal = True
                
                # Asignar 30 consultas al usuario
                instance.consultas_restantes = 30
                
                # Verificar si ya existe una suscripción
                suscripcion, creada = Suscripcion.objects.get_or_create(
                    usuario=instance,
                    defaults={
                        'activo': True,
                        'fecha_inicio': timezone.now(),
                        'fecha_expiracion': timezone.now() + timezone.timedelta(days=30),
                        'origen_pago': 'Manual'
                    }
                )
                
                # Si ya existía pero estaba inactiva, reactivarla
                if not creada and not suscripcion.activo:
                    suscripcion.activo = True
                    suscripcion.fecha_ultima_renovacion = timezone.now()
                    suscripcion.fecha_expiracion = timezone.now() + timezone.timedelta(days=30)
                    suscripcion.save()
                
                procesando_signal = False
            
            # Detectar si el campo 'suscrito' cambió a False
            elif not instance.suscrito and usuario_anterior.suscrito:
                procesando_signal = True
                
                # Buscar y desactivar la suscripción si existe
                try:
                    suscripcion = Suscripcion.objects.get(usuario=instance)
                    suscripcion.activo = False
                    suscripcion.renovacion_automatica = False
                    suscripcion.save()
                except Suscripcion.DoesNotExist:
                    pass
                
                procesando_signal = False
    except User.DoesNotExist:
        # Es un usuario nuevo, no hacemos nada
        pass

@receiver(post_save, sender=Suscripcion)
def sincronizar_suscripcion_a_usuario(sender, instance, created, **kwargs):
    """
    Signal que se activa cuando se guarda una suscripción.
    Sincroniza el estado de la suscripción con el usuario.
    """
    global procesando_signal
    
    # Evitar recursión infinita
    if procesando_signal:
        return
    
    procesando_signal = True
    
    usuario = instance.usuario
    
    # Actualizar el estado 'suscrito' del usuario para que coincida con 'activo' de la suscripción
    if usuario.suscrito != instance.activo:
        usuario.suscrito = instance.activo
        
        # Si se está activando la suscripción, asignar 30 consultas
        if instance.activo and (created or usuario.consultas_restantes == 0):
            usuario.consultas_restantes = 30
            
        usuario.save()
    
    procesando_signal = False