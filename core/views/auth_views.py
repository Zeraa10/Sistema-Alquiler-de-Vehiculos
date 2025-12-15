from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect
from django.views import View
from core.models import Cliente
from core.forms import ClienteForm


class RegisterView(View):
    """Registro para clientes"""
    def get(self, request):
        form = ClienteForm()
        return render(request, 'auth/register.html', {'form': form})

    def post(self, request):
        form = ClienteForm(request.POST)
        if form.is_valid():
            # Obtener datos del formulario
            nombre = form.cleaned_data.get('nombre')
            apellido = form.cleaned_data.get('apellido')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            licencia = form.cleaned_data.get('licencia')
            telefono = form.cleaned_data.get('telefono', '')
            
            # Crear usuario Django
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password
            )
            
            # Crear Cliente asociado al User
            Cliente.objects.create(
                user=user,
                nombre=nombre,
                apellido=apellido,
                licencia=licencia,
                telefono=telefono
            )
            
            return redirect('login')
        return render(request, 'auth/register.html', {'form': form})


class LoginView(View):
    """Login para Admin y Cliente"""
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'auth/login.html', {'form': form})

    def post(self, request):
        email = request.POST.get('username')  # Usar email como username
        password = request.POST.get('password')
        
        if not email or not password:
            return render(request, 'auth/login.html', {
                'error': 'Por favor ingresa email y contraseña'
            })
        
        # Intentar autenticar
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            
            # Redirigir según rol
            if user.is_staff or user.is_superuser:
                return redirect('panel_admin')
            else:
                return redirect('panel_cliente')
        else:
            return render(request, 'auth/login.html', {
                'error': 'Email o contraseña incorrectos'
            })


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('home')
