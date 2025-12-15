from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from core.models import SubcategoriaLicencia
from core.forms import SubcategoriaLicenciaForm
from core.mixins import AdminRequiredMixin

class SubcategoriaLicenciaList(AdminRequiredMixin, ListView):
    model = SubcategoriaLicencia
    template_name = 'subcategoria_licencia/list.html'

class SubcategoriaLicenciaDetail(AdminRequiredMixin, DetailView):
    model = SubcategoriaLicencia
    template_name = 'subcategoria_licencia/detail.html'

class SubcategoriaLicenciaCreate(AdminRequiredMixin, CreateView):
    model = SubcategoriaLicencia
    form_class = SubcategoriaLicenciaForm
    template_name = 'subcategoria_licencia/form.html'
    success_url = reverse_lazy('subcategoria_licencia_list')

class SubcategoriaLicenciaUpdate(AdminRequiredMixin, UpdateView):
    model = SubcategoriaLicencia
    form_class = SubcategoriaLicenciaForm
    template_name = 'subcategoria_licencia/form.html'
    success_url = reverse_lazy('subcategoria_licencia_list')

class SubcategoriaLicenciaDelete(AdminRequiredMixin, DeleteView):
    model = SubcategoriaLicencia
    template_name = 'subcategoria_licencia/confirm_delete.html'
    success_url = reverse_lazy('subcategoria_licencia_list')
