from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from core.models import CategoriaLicencia
from core.forms import CategoriaLicenciaForm
from core.mixins import AdminRequiredMixin

class CategoriaLicenciaList(AdminRequiredMixin, ListView):
    model = CategoriaLicencia
    template_name = 'categoria_licencia/list.html'

class CategoriaLicenciaDetail(AdminRequiredMixin, DetailView):
    model = CategoriaLicencia
    template_name = 'categoria_licencia/detail.html'

class CategoriaLicenciaCreate(AdminRequiredMixin, CreateView):
    model = CategoriaLicencia
    form_class = CategoriaLicenciaForm
    template_name = 'categoria_licencia/form.html'
    success_url = reverse_lazy('categoria_licencia_list')

class CategoriaLicenciaUpdate(AdminRequiredMixin, UpdateView):
    model = CategoriaLicencia
    form_class = CategoriaLicenciaForm
    template_name = 'categoria_licencia/form.html'
    success_url = reverse_lazy('categoria_licencia_list')

class CategoriaLicenciaDelete(AdminRequiredMixin, DeleteView):
    model = CategoriaLicencia
    template_name = 'categoria_licencia/confirm_delete.html'
    success_url = reverse_lazy('categoria_licencia_list')
