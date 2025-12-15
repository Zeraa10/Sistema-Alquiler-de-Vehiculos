from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.db.models import Q
from core.models import Reserva
from core.forms import ReservaForm, FiltroReservaForm, ReservaAprobacionForm
from core.mixins import AdminRequiredMixin

class ReservaList(AdminRequiredMixin, ListView):
    model = Reserva
    template_name = 'reserva/list.html'
    
    def get_queryset(self):
        queryset = Reserva.objects.all()
        forma = FiltroReservaForm(self.request.GET)
        
        if forma.is_valid():
            cliente_nombre = forma.cleaned_data.get('cliente_nombre')
            marca_vehiculo = forma.cleaned_data.get('marca_vehiculo')
            estado = forma.cleaned_data.get('estado')
            fecha_inicio_desde = forma.cleaned_data.get('fecha_inicio_desde')
            fecha_inicio_hasta = forma.cleaned_data.get('fecha_inicio_hasta')
            
            if cliente_nombre:
                queryset = queryset.filter(
                    Q(cliente__nombre__icontains=cliente_nombre) |
                    Q(cliente__apellido__icontains=cliente_nombre)
                )
            if marca_vehiculo:
                queryset = queryset.filter(vehiculo__marca__icontains=marca_vehiculo)
            if estado:
                queryset = queryset.filter(estado=estado)
            if fecha_inicio_desde:
                queryset = queryset.filter(fecha_inicio__gte=fecha_inicio_desde)
            if fecha_inicio_hasta:
                queryset = queryset.filter(fecha_inicio__lte=fecha_inicio_hasta)
        
        return queryset.order_by('-fecha_inicio')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = FiltroReservaForm(self.request.GET)
        return context

class ReservaDetail(AdminRequiredMixin, DetailView):
    model = Reserva
    template_name = 'reserva/detail.html'

class ReservaCreate(AdminRequiredMixin, CreateView):
    model = Reserva
    form_class = ReservaForm
    template_name = 'reserva/form.html'
    success_url = reverse_lazy('reserva_list')
    
    def form_valid(self, form):
        # Guardar la reserva
        reserva = form.save()
        
        # Actualizar disponibilidad del vehículo basado en reservas activas
        vehiculo = reserva.vehiculo
        if reserva.estado in ['pendiente', 'confirmada']:
            vehiculo.disponible = False
            vehiculo.save()
            
            # Crear factura automáticamente si está confirmada
            if reserva.estado == 'confirmada':
                reserva.crear_factura_automatica()
        
        return super().form_valid(form)

class ReservaUpdate(AdminRequiredMixin, UpdateView):
    model = Reserva
    form_class = ReservaAprobacionForm
    template_name = 'reserva/form.html'
    success_url = reverse_lazy('reserva_list')
    
    def form_valid(self, form):
        # Obtener estado anterior y nuevo
        reserva = self.get_object()
        estado_anterior = reserva.estado
        
        # Guardar la reserva con nuevo estado
        reserva = form.save(commit=False)
        vehiculo = reserva.vehiculo
        
        # Si cambió a confirmada desde pendiente
        if estado_anterior == 'pendiente' and reserva.estado == 'confirmada':
            vehiculo.disponible = False
            vehiculo.save()
            
            # Crear factura automáticamente
            reserva.save()
            reserva.crear_factura_automatica()
            messages.success(self.request, f'Reserva confirmada. Factura creada automáticamente.')
        
        # Si cambió a cancelada
        elif reserva.estado == 'cancelada':
            # Verificar si hay otras reservas activas
            reservas_activas = Reserva.objects.filter(
                vehiculo=vehiculo,
                estado__in=['pendiente', 'confirmada']
            ).exclude(pk=reserva.pk).exists()
            
            vehiculo.disponible = not reservas_activas
            vehiculo.save()
            reserva.save()
            messages.success(self.request, 'Reserva cancelada.')
        
        else:
            # Para otros cambios de estado
            if reserva.estado in ['pendiente', 'confirmada']:
                vehiculo.disponible = False
                vehiculo.save()
            
            reserva.save()
        
        return super().form_valid(form)

class ReservaDelete(AdminRequiredMixin, DeleteView):
    model = Reserva
    template_name = 'reserva/confirm_delete.html'
    success_url = reverse_lazy('reserva_list')
    
    def delete(self, request, *args, **kwargs):
        # Obtener la reserva antes de eliminarla
        reserva = self.get_object()
        vehiculo = reserva.vehiculo
        
        # Eliminar la reserva
        response = super().delete(request, *args, **kwargs)
        
        # Verificar si hay otras reservas activas para este vehículo
        reservas_activas = Reserva.objects.filter(
            vehiculo=vehiculo,
            estado__in=['pendiente', 'confirmada']
        ).exists()
        
        # Si no hay reservas activas, marcar como disponible
        if not reservas_activas:
            vehiculo.disponible = True
            vehiculo.save()
        
        return response
