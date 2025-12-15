from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin para requerir que el usuario sea administrador"""
    login_url = 'login'
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            # Si está autenticado pero no es admin, redirigir al panel de cliente
            return redirect('panel_cliente')
        return super().handle_no_permission()
