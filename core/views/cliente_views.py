from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from core.models import Cliente
from core.forms import ClienteForm, FiltroClienteForm
from core.mixins import AdminRequiredMixin

class ClienteList(AdminRequiredMixin, ListView):
    model = Cliente
    template_name = 'cliente/list.html'
    
    def get_queryset(self):
        queryset = Cliente.objects.all()
        forma = FiltroClienteForm(self.request.GET)
        
        if forma.is_valid():
            nombre = forma.cleaned_data.get('nombre')
            apellido = forma.cleaned_data.get('apellido')
            email = forma.cleaned_data.get('email')
            licencia = forma.cleaned_data.get('licencia')
            
            if nombre:
                queryset = queryset.filter(nombre__icontains=nombre)
            if apellido:
                queryset = queryset.filter(apellido__icontains=apellido)
            if email:
                queryset = queryset.filter(user__email__icontains=email)
            if licencia:
                queryset = queryset.filter(licencia=licencia)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = FiltroClienteForm(self.request.GET)
        return context

class ClienteDetail(AdminRequiredMixin, DetailView):
    model = Cliente
    template_name = 'cliente/detail.html'

class ClienteCreate(AdminRequiredMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'cliente/form.html'
    success_url = reverse_lazy('cliente_list')

class ClienteUpdate(AdminRequiredMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'cliente/form.html'
    success_url = reverse_lazy('cliente_list')

class ClienteDelete(AdminRequiredMixin, DeleteView):
    model = Cliente
    template_name = 'cliente/confirm_delete.html'
    success_url = reverse_lazy('cliente_list')
