from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from core.models import Cliente


class PanelClienteView(LoginRequiredMixin, TemplateView):
    """Panel para clientes registrados"""
    template_name = 'panel_cliente.html'
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        # Verificar si es un cliente registrado (no admin)
        try:
            cliente = request.user.cliente
        except Cliente.DoesNotExist:
            cliente = None
        
        # Si es admin, redirigir al panel de admin
        if request.user.is_staff or request.user.is_superuser:
            return redirect('panel_admin')
        
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Buscar el cliente actual
        try:
            context['cliente'] = self.request.user.cliente
        except Cliente.DoesNotExist:
            context['cliente'] = None
        
        return context


class PanelAdminView(LoginRequiredMixin, TemplateView):
    """Panel de administración para staff/superuser"""
    template_name = 'panel_admin.html'
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        # Verificar que sea admin
        if not (request.user.is_staff or request.user.is_superuser):
            return redirect('panel_cliente')
        
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context
