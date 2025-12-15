from django.contrib import admin
from .models import CategoriaLicencia, SubcategoriaLicencia, Cliente, Vehiculo, Reserva, Devolucion, Factura

@admin.register(CategoriaLicencia)
class CategoriaLicenciaAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo', 'descripcion')
    search_fields = ('codigo', 'descripcion')

@admin.register(SubcategoriaLicencia)
class SubcategoriaLicenciaAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo', 'descripcion', 'categoria')
    search_fields = ('codigo', 'descripcion')
    list_filter = ('categoria',)

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'apellido', 'get_email', 'telefono', 'licencia')
    search_fields = ('nombre', 'apellido', 'user__email')
    list_filter = ('licencia',)
    
    def get_email(self, obj):
        return obj.user.email if obj.user else 'Sin email'
    get_email.short_description = 'Email'

@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('id', 'marca', 'modelo', 'placa', 'color', 'costo_dia', 'disponible')
    search_fields = ('marca', 'modelo', 'placa', 'color')
    list_filter = ('disponible',)

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id', 'vehiculo', 'cliente', 'fecha_inicio', 'fecha_fin', 'total', 'estado')
    search_fields = ('vehiculo__placa', 'cliente__nombre', 'cliente__apellido')
    list_filter = ('estado',)

@admin.register(Devolucion)
class DevolucionAdmin(admin.ModelAdmin):
    list_display = ('id', 'reserva', 'fecha_devolucion', 'estado_devolucion', 'penalizacion')
    list_filter = ('estado_devolucion',)

@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ('id', 'numero', 'reserva', 'monto', 'fecha_emision')
    search_fields = ('numero',)
