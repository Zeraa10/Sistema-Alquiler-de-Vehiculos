from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.db.models import Q
from core.models import Devolucion
from core.forms import DevolucionForm, FiltroDevolucionForm
from core.mixins import AdminRequiredMixin

class DevolucionList(AdminRequiredMixin, ListView):
    model = Devolucion
    template_name = 'devolucion/list.html'
    
    def get_queryset(self):
        queryset = Devolucion.objects.all()
        forma = FiltroDevolucionForm(self.request.GET)
        
        if forma.is_valid():
            estado_devolucion = forma.cleaned_data.get('estado_devolucion')
            fecha_desde = forma.cleaned_data.get('fecha_desde')
            fecha_hasta = forma.cleaned_data.get('fecha_hasta')
            penalizacion_min = forma.cleaned_data.get('penalizacion_min')
            penalizacion_max = forma.cleaned_data.get('penalizacion_max')
            
            if estado_devolucion:
                queryset = queryset.filter(estado_devolucion=estado_devolucion)
            if fecha_desde:
                queryset = queryset.filter(fecha_devolucion__gte=fecha_desde)
            if fecha_hasta:
                queryset = queryset.filter(fecha_devolucion__lte=fecha_hasta)
            if penalizacion_min is not None:
                queryset = queryset.filter(penalizacion__gte=penalizacion_min)
            if penalizacion_max is not None:
                queryset = queryset.filter(penalizacion__lte=penalizacion_max)
        
        return queryset.order_by('-fecha_devolucion')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = FiltroDevolucionForm(self.request.GET)
        return context

class DevolucionDetail(AdminRequiredMixin, DetailView):
    model = Devolucion
    template_name = 'devolucion/detail.html'

class DevolucionCreate(AdminRequiredMixin, CreateView):
    model = Devolucion
    form_class = DevolucionForm
    template_name = 'devolucion/form.html'
    success_url = reverse_lazy('devolucion_list')
    
    def form_valid(self, form):
        devolucion = form.save(commit=False)
        
        # Calcular penalización automáticamente
        devolucion.calcular_penalizacion()
        devolucion.save()
        
        # Actualizar factura con penalización
        devolucion.actualizar_factura_con_penalizacion()
        
        # Marcar vehículo como disponible nuevamente
        devolucion.reserva.vehiculo.disponible = True
        devolucion.reserva.vehiculo.save()
        
        messages.success(self.request, f'Devolución registrada. Penalización: ${devolucion.penalizacion:,.2f}')
        return super().form_valid(form)

class DevolucionUpdate(AdminRequiredMixin, UpdateView):
    model = Devolucion
    form_class = DevolucionForm
    template_name = 'devolucion/form.html'
    success_url = reverse_lazy('devolucion_list')
    
    def form_valid(self, form):
        devolucion = form.save(commit=False)
        
        # Recalcular penalización
        devolucion.calcular_penalizacion()
        devolucion.save()
        
        # Actualizar factura
        devolucion.actualizar_factura_con_penalizacion()
        
        messages.success(self.request, f'Devolución actualizada. Penalización: ${devolucion.penalizacion:,.2f}')
        return super().form_valid(form)

class DevolucionDelete(AdminRequiredMixin, DeleteView):
    model = Devolucion
    template_name = 'devolucion/confirm_delete.html'
    success_url = reverse_lazy('devolucion_list')
