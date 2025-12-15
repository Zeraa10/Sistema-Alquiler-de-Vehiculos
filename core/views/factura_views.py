from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from core.models import Factura
from core.forms import FacturaForm, FiltroFacturaForm
from core.mixins import AdminRequiredMixin

class FacturaList(AdminRequiredMixin, ListView):
    model = Factura
    template_name = 'factura/list.html'
    
    def get_queryset(self):
        queryset = Factura.objects.all()
        forma = FiltroFacturaForm(self.request.GET)
        
        if forma.is_valid():
            numero = forma.cleaned_data.get('numero')
            monto_min = forma.cleaned_data.get('monto_min')
            monto_max = forma.cleaned_data.get('monto_max')
            fecha_desde = forma.cleaned_data.get('fecha_desde')
            fecha_hasta = forma.cleaned_data.get('fecha_hasta')
            
            if numero:
                queryset = queryset.filter(numero__icontains=numero)
            if monto_min is not None:
                queryset = queryset.filter(monto__gte=monto_min)
            if monto_max is not None:
                queryset = queryset.filter(monto__lte=monto_max)
            if fecha_desde:
                queryset = queryset.filter(fecha_emision__gte=fecha_desde)
            if fecha_hasta:
                queryset = queryset.filter(fecha_emision__lte=fecha_hasta)
        
        return queryset.order_by('-fecha_emision')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = FiltroFacturaForm(self.request.GET)
        return context

class FacturaDetail(AdminRequiredMixin, DetailView):
    model = Factura
    template_name = 'factura/detail.html'

class FacturaCreate(AdminRequiredMixin, CreateView):
    model = Factura
    form_class = FacturaForm
    template_name = 'factura/form.html'
    success_url = reverse_lazy('factura_list')

class FacturaUpdate(AdminRequiredMixin, UpdateView):
    model = Factura
    form_class = FacturaForm
    template_name = 'factura/form.html'
    success_url = reverse_lazy('factura_list')

class FacturaDelete(AdminRequiredMixin, DeleteView):
    model = Factura
    template_name = 'factura/confirm_delete.html'
    success_url = reverse_lazy('factura_list')
