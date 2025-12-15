from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from core.models import (
    CategoriaLicencia,
    SubcategoriaLicencia,
    Cliente,
    Vehiculo,
    Reserva,
    Devolucion,
    Factura,
)

# Formulario para CategoriaLicencia
class CategoriaLicenciaForm(forms.ModelForm):
    class Meta:
        model = CategoriaLicencia
        fields = ['codigo', 'descripcion']

# Formulario para SubcategoriaLicencia
class SubcategoriaLicenciaForm(forms.ModelForm):
    class Meta:
        model = SubcategoriaLicencia
        fields = ['codigo', 'descripcion', 'categoria']

# Formulario para Cliente
class ClienteForm(forms.ModelForm):
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Contraseña', help_text='Ingresa una contraseña segura')

    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'licencia', 'telefono']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(username=email).exists():
            raise ValidationError("Este email ya está registrado.")
        return email

# Formulario para Vehiculo
class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ['marca', 'modelo', 'placa', 'costo_dia', 'color', 'disponible', 'imagen']
        widgets = {
            'imagen': forms.FileInput(attrs={'accept': 'image/*'}),
        }

# Formulario para Reserva
class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['vehiculo', 'cliente', 'fecha_inicio', 'fecha_fin', 'total', 'estado']

    def clean(self):
        cleaned_data = super().clean()
        vehiculo = cleaned_data.get('vehiculo')
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')

        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            raise ValidationError("La fecha de fin debe ser posterior a la fecha de inicio.")

        if vehiculo and fecha_inicio and fecha_fin:
            conflicto = Reserva.objects.filter(
                vehiculo=vehiculo,
                estado__in=['pendiente', 'confirmada'],
                fecha_fin__gte=fecha_inicio,
                fecha_inicio__lte=fecha_fin
            ).exists()
            if conflicto:
                raise ValidationError("El vehículo está reservado en las fechas seleccionadas.")

        return cleaned_data

# Formulario para que ADMIN apruebe/rechace reservas (solo estado)
class ReservaAprobacionForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['estado']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-control'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limitar opciones a solo confirmada o cancelada
        self.fields['estado'].choices = [
            ('pendiente', 'Pendiente'),
            ('confirmada', 'Confirmar ✓'),
            ('cancelada', 'Cancelar ✗'),
        ]

# Formulario para Devolucion
class DevolucionForm(forms.ModelForm):
    class Meta:
        model = Devolucion
        fields = ['reserva', 'fecha_devolucion', 'estado_devolucion']

    def clean_fecha_devolucion(self):
        fecha_devolucion = self.cleaned_data.get('fecha_devolucion')
        reserva = self.cleaned_data.get('reserva')
        if reserva and fecha_devolucion and fecha_devolucion < reserva.fecha_inicio:
            raise ValidationError("La fecha de devolución no puede ser anterior a la fecha de inicio de la reserva.")
        return fecha_devolucion

# Formulario para Factura
class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = ['reserva', 'numero', 'monto', 'fecha_emision']

    def clean_numero(self):
        numero = self.cleaned_data.get('numero')
        qs = Factura.objects.filter(numero=numero)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("El número de factura ya existe.")
        return numero

# Formulario para Reserva desde el panel de cliente (sin campo cliente)
class ClienteReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['vehiculo', 'fecha_inicio', 'fecha_fin', 'total']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar vehículos disponibles
        self.fields['vehiculo'].queryset = Vehiculo.objects.filter(disponible=True)
        self.fields['vehiculo'].label = 'Vehículo'
        self.fields['fecha_inicio'].label = 'Fecha de Inicio'
        self.fields['fecha_fin'].label = 'Fecha de Fin'
        self.fields['total'].label = 'Total (COP)'
        
        # Personalizar el texto de las opciones del vehículo para mostrar el precio
        choices = []
        for vehiculo in Vehiculo.objects.filter(disponible=True):
            label = f"{vehiculo.marca} {vehiculo.modelo} - {vehiculo.placa} - ${vehiculo.costo_dia:,.0f}"
            choices.append((vehiculo.id, label))
        self.fields['vehiculo'].choices = choices

    def clean(self):
        cleaned_data = super().clean()
        vehiculo = cleaned_data.get('vehiculo')
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')

        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            raise ValidationError("La fecha de fin debe ser posterior a la fecha de inicio.")

        if vehiculo and fecha_inicio and fecha_fin:
            conflicto = Reserva.objects.filter(
                vehiculo=vehiculo,
                estado__in=['pendiente', 'confirmada'],
                fecha_fin__gte=fecha_inicio,
                fecha_inicio__lte=fecha_fin
            ).exists()
            if conflicto:
                raise ValidationError("El vehículo está reservado en las fechas seleccionadas.")

        return cleaned_data

# Formulario para Devolución desde cliente (solo selecciona reserva propia)
class ClienteDevolucionForm(forms.ModelForm):
    class Meta:
        model = Devolucion
        fields = ['fecha_devolucion', 'estado_devolucion']
        widgets = {
            'fecha_devolucion': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_fecha_devolucion(self):
        fecha_devolucion = self.cleaned_data.get('fecha_devolucion')
        reserva = self.instance.reserva if hasattr(self.instance, 'reserva') else None
        if reserva and fecha_devolucion and fecha_devolucion < reserva.fecha_inicio:
            raise ValidationError("La fecha de devolución no puede ser anterior a la fecha de inicio de la reserva.")
        return fecha_devolucion

# Formulario para editar perfil del cliente
class ClientePerfilForm(forms.ModelForm):
    email = forms.EmailField(label='Email', required=True)
    password = forms.CharField(widget=forms.PasswordInput, label='Nueva Contraseña (opcional)', required=False, help_text='Dejar en blanco para no cambiar la contraseña')

    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'licencia', 'telefono']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Comprobar que no exista otro User con ese email
        qs = User.objects.filter(email=email)
        # Si estamos editando, permitir mantener el correo propio
        if self.instance.pk and hasattr(self.instance, 'user') and self.instance.user:
            qs = qs.exclude(pk=self.instance.user.pk)
        if qs.exists():
            raise ValidationError('Este email ya está registrado.')
        return email

    def save(self, commit=True):
        instance = super().save(commit=False)
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        # Si el cliente ya tiene un usuario asociado, actualizarlo
        if hasattr(instance, 'user') and instance.user:
            user = instance.user
            if email and user.email != email:
                user.email = email
                user.username = email
            if password:
                user.set_password(password)
            user.save()
        else:
            # Crear usuario si no existe
            username = email if email else f'user{instance.pk or "new"}'
            user = User.objects.create_user(username=username, email=email)
            if password:
                user.set_password(password)
            user.save()
            instance.user = user

        if commit:
            instance.save()
        return instance
        
        if commit:
            instance.save()
        return instance


# ==================== FORMULARIOS DE FILTRO ====================

# Filtro para Vehículos
class FiltroVehiculoForm(forms.Form):
    marca = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Marca', 'class': 'filter-input'})
    )
    modelo = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Modelo', 'class': 'filter-input'})
    )
    precio_min = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Precio mínimo', 'class': 'filter-input', 'step': '0.01'})
    )
    precio_max = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Precio máximo', 'class': 'filter-input', 'step': '0.01'})
    )
    disponible = forms.NullBooleanField(
        required=False,
        widget=forms.Select(
            choices=[('', 'Todos'), ('true', 'Solo disponibles'), ('false', 'Solo no disponibles')],
            attrs={'class': 'filter-input'}
        )
    )


# Filtro para Clientes
class FiltroClienteForm(forms.Form):
    nombre = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Nombre', 'class': 'filter-input'})
    )
    apellido = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Apellido', 'class': 'filter-input'})
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'filter-input'})
    )
    licencia = forms.ModelChoiceField(
        queryset=SubcategoriaLicencia.objects.all(),
        required=False,
        empty_label='Todas las licencias',
        widget=forms.Select(attrs={'class': 'filter-input'})
    )


# Filtro para Reservas
class FiltroReservaForm(forms.Form):
    ESTADO_CHOICES = [('', 'Todos'), ('pendiente', 'Pendiente'), ('confirmada', 'Confirmada'), ('cancelada', 'Cancelada')]
    
    cliente_nombre = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Nombre del cliente', 'class': 'filter-input'})
    )
    marca_vehiculo = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Marca del vehículo', 'class': 'filter-input'})
    )
    estado = forms.ChoiceField(
        choices=ESTADO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'filter-input'})
    )
    fecha_inicio_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'filter-input'})
    )
    fecha_inicio_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'filter-input'})
    )


# Filtro para Facturas
class FiltroFacturaForm(forms.Form):
    numero = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Número de factura', 'class': 'filter-input'})
    )
    monto_min = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Monto mínimo', 'class': 'filter-input', 'step': '0.01'})
    )
    monto_max = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Monto máximo', 'class': 'filter-input', 'step': '0.01'})
    )
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'filter-input'})
    )
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'filter-input'})
    )


# Filtro para Devoluciones
class FiltroDevolucionForm(forms.Form):
    ESTADO_DEVOLUCION_CHOICES = [('', 'Todos'), ('entregado', 'Entregado'), ('atrasado', 'Atrasado'), ('danado', 'Dañado')]
    
    estado_devolucion = forms.ChoiceField(
        choices=ESTADO_DEVOLUCION_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'filter-input'})
    )
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'filter-input'})
    )
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'filter-input'})
    )
    penalizacion_min = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Penalización mínima', 'class': 'filter-input', 'step': '0.01'})
    )
    penalizacion_max = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Penalización máxima', 'class': 'filter-input', 'step': '0.01'})
    )