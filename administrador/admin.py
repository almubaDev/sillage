from django.contrib import admin
from .models import Suscripcion, HistorialPago

class SuscripcionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'activo', 'fecha_inicio', 'fecha_expiracion', 'monto', 'moneda', 'origen_pago')
    list_filter = ('activo', 'renovacion_automatica')
    search_fields = ('usuario__email',)
    date_hierarchy = 'fecha_inicio'
    fieldsets = (
        ('Usuario', {
            'fields': ('usuario', 'activo')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_expiracion', 'fecha_ultima_renovacion')
        }),
        ('Económico', {
            'fields': ('monto', 'moneda', 'origen_pago', 'referencia_pago')
        }),
        ('Configuración', {
            'fields': ('renovacion_automatica',)
        }),
    )

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

admin.site.register(Suscripcion, SuscripcionAdmin)
admin.site.register(HistorialPago, HistorialPagoAdmin)