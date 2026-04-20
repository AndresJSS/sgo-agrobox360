from django.contrib import admin
from .models import Cultivo, Insumo, Tarea

# Configuración de las tablas
@admin.register(Cultivo)
class CultivoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'variedad', 'estado', 'fecha_siembra')
    list_filter = ('estado',)
    search_fields = ('nombre',)

@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'stock_actual', 'unidad', 'stock_minimo')
    search_fields = ('nombre',)

@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'prioridad', 'subsistema', 'completada', 'fecha_creacion')
    list_filter = ('completada', 'prioridad', 'subsistema')
    search_fields = ('titulo', 'descripcion')

#@admin.register(RegistroOperativo)
#class RegistroOperativoAdmin(admin.ModelAdmin):
#    list_display = ('timestamp', 'accion', 'firmado_por')
#    readonly_fields = ('timestamp', 'accion', 'firmado_por', 'descripcion', 'ip_origen')
    # Inmutabilidad básica del historial
#    def has_add_permission(self, request):
#        return False
#    def has_delete_permission(self, request, obj = None):
#        return False

