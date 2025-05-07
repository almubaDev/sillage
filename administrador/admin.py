from django.contrib import admin
from .models import Suscripcion, HistorialPago

@admin.register(Suscripcion)
class SuscripcionAdmin(admin.ModelAdmin):
    list_display = (
        'usuario', 'activo', 'fecha_inicio', 'fecha_expiracion',
        'origen_pago', 'monto', 'moneda', 'renovacion_automatica', 'flow_customer_id'
    )
    list_filter = ('activo', 'renovacion_automatica', 'moneda')
    search_fields = ('usuario__username', 'usuario__email', 'flow_customer_id')
    readonly_fields = ('fecha_inicio', 'fecha_ultima_renovacion', 'ultima_actualizacion')

    fieldsets = (
        ('Información del usuario', {
            'fields': ('usuario',)
        }),
        ('Estado de la suscripción', {
            'fields': ('activo', 'fecha_inicio', 'fecha_expiracion', 'fecha_ultima_renovacion')
        }),
        ('Pago', {
            'fields': ('origen_pago', 'referencia_pago', 'monto', 'moneda', 'flow_customer_id')
        }),
        ('Configuración', {
            'fields': ('renovacion_automatica',)
        }),
        ('Auditoría', {
            'fields': ('ultima_actualizacion',)
        }),
    )

@admin.register(HistorialPago)
class HistorialPagoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fecha_pago', 'monto', 'moneda', 'metodo_pago', 'estado')
    list_filter = ('estado', 'metodo_pago')
    search_fields = ('usuario__email', 'referencia')
    date_hierarchy = 'fecha_pago'
    fieldsets = (
        ('Usuario', {
            'fields': ('usuario', 'suscripcion')
        }),
        ('Información del pago', {
            'fields': ('fecha_pago', 'monto', 'moneda', 'metodo_pago', 'referencia')
        }),
        ('Estado', {
            'fields': ('estado', 'notas')
        }),
    )
