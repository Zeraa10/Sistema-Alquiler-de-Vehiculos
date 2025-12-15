from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from core.models import Vehiculo
from core.forms import VehiculoForm, FiltroVehiculoForm
from core.mixins import AdminRequiredMixin

class VehiculoList(AdminRequiredMixin, ListView):
    model = Vehiculo
    template_name = 'vehiculo/list.html'
    
    def get_queryset(self):
        queryset = Vehiculo.objects.all()
        forma = FiltroVehiculoForm(self.request.GET)
        
        if forma.is_valid():
            marca = forma.cleaned_data.get('marca')
            modelo = forma.cleaned_data.get('modelo')
            precio_min = forma.cleaned_data.get('precio_min')
            precio_max = forma.cleaned_data.get('precio_max')
            disponible = forma.cleaned_data.get('disponible')
            
            if marca:
                queryset = queryset.filter(marca__icontains=marca)
            if modelo:
                queryset = queryset.filter(modelo__icontains=modelo)
            if precio_min is not None:
                queryset = queryset.filter(costo_dia__gte=precio_min)
            if precio_max is not None:
                queryset = queryset.filter(costo_dia__lte=precio_max)
            if disponible is not None:
                queryset = queryset.filter(disponible=disponible)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = FiltroVehiculoForm(self.request.GET)
        return context

class VehiculoDetail(AdminRequiredMixin, DetailView):
    model = Vehiculo
    template_name = 'vehiculo/detail.html'

class VehiculoCreate(AdminRequiredMixin, CreateView):
    model = Vehiculo
    form_class = VehiculoForm
    template_name = 'vehiculo/form.html'
    success_url = reverse_lazy('vehiculo_list')

class VehiculoUpdate(AdminRequiredMixin, UpdateView):
    model = Vehiculo
    form_class = VehiculoForm
    template_name = 'vehiculo/form.html'
    success_url = reverse_lazy('vehiculo_list')

class VehiculoDelete(AdminRequiredMixin, DeleteView):
    model = Vehiculo
    template_name = 'vehiculo/confirm_delete.html'
    success_url = reverse_lazy('vehiculo_list')
