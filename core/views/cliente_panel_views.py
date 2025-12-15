from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from core.models import Cliente, Vehiculo, Reserva, Factura, Devolucion
from core.forms import ClienteReservaForm, ClientePerfilForm, FiltroVehiculoForm, FiltroReservaForm, FiltroFacturaForm, FiltroDevolucionForm, ClienteDevolucionForm


class ClienteVehiculosListView(LoginRequiredMixin, ListView):
    """Lista de vehículos disponibles para el cliente"""
    model = Vehiculo
    template_name = 'cliente_panel/vehiculos_list.html'
    context_object_name = 'vehiculos'
    login_url = 'login'

    def get_queryset(self):
        # Mostrar todos los vehículos (por defecto disponibles, pero permite filtrar)
        queryset = Vehiculo.objects.all().order_by('-disponible', 'marca')
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
        else:
            # Si no hay filtros, mostrar solo disponibles por defecto
            queryset = queryset.filter(disponible=True)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['cliente'] = self.request.user.cliente
        except Cliente.DoesNotExist:
            context['cliente'] = None
        context['form'] = FiltroVehiculoForm(self.request.GET)
        return context


class ClienteNuevaReservaView(LoginRequiredMixin, CreateView):
    """Crear nueva reserva para el cliente autenticado"""
    model = Reserva
    form_class = ClienteReservaForm
    template_name = 'cliente_panel/nueva_reserva.html'
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        # Verificar que sea cliente, no admin
        if request.user.is_staff or request.user.is_superuser:
            return redirect('panel_admin')
        return super().get(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        # Pre-seleccionar vehículo si viene como parámetro
        vehiculo_id = self.request.GET.get('vehiculo')
        if vehiculo_id:
            try:
                initial['vehiculo'] = int(vehiculo_id)
            except (ValueError, TypeError):
                pass
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['cliente'] = self.request.user.cliente
        except Cliente.DoesNotExist:
            context['cliente'] = None
        
        # Agregar vehículo seleccionado si existe
        vehiculo_id = self.request.GET.get('vehiculo')
        if vehiculo_id:
            try:
                context['vehiculo_seleccionado'] = Vehiculo.objects.get(pk=vehiculo_id, disponible=True)
            except Vehiculo.DoesNotExist:
                context['vehiculo_seleccionado'] = None
        else:
            context['vehiculo_seleccionado'] = None
        
        # Agregar lista de vehículos para el JavaScript
        context['vehiculos'] = Vehiculo.objects.filter(disponible=True)
        
        return context

    def form_valid(self, form):
        # Asignar automáticamente el cliente autenticado
        try:
            cliente = self.request.user.cliente
            form.instance.cliente = cliente
            form.instance.estado = 'pendiente'
            
            # Calcular total automáticamente si no se proporcionó
            if not form.instance.total or form.instance.total == 0:
                vehiculo = form.instance.vehiculo
                fecha_inicio = form.instance.fecha_inicio
                fecha_fin = form.instance.fecha_fin
                if vehiculo and fecha_inicio and fecha_fin:
                    dias = (fecha_fin - fecha_inicio).days + 1
                    form.instance.total = vehiculo.costo_dia * dias
            
            # Guardar la reserva
            reserva = form.save()
            
            # Actualizar disponibilidad del vehículo basado en reservas activas
            vehiculo = reserva.vehiculo
            reservas_activas = Reserva.objects.filter(
                vehiculo=vehiculo,
                estado__in=['pendiente', 'confirmada']
            ).exclude(pk=reserva.pk).exists()
            
            if reservas_activas or reserva.estado in ['pendiente', 'confirmada']:
                vehiculo.disponible = False
                vehiculo.save()
            
            # Crear factura automáticamente si está confirmada
            if reserva.estado == 'confirmada':
                reserva.crear_factura_automatica()
            
            messages.success(self.request, 'Reserva creada exitosamente. Está pendiente de confirmación.')
            return super().form_valid(form)
        except Cliente.DoesNotExist:
            messages.error(self.request, 'Error: No se encontró tu perfil de cliente.')
            return redirect('panel_cliente')

    def get_success_url(self):
        return reverse_lazy('cliente_vehiculos')


class ClienteMisReservasListView(LoginRequiredMixin, ListView):
    """Lista de reservas del cliente autenticado"""
    model = Reserva
    template_name = 'cliente_panel/mis_reservas.html'
    context_object_name = 'reservas'
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        # Verificar que sea cliente, no admin
        if request.user.is_staff or request.user.is_superuser:
            return redirect('panel_admin')
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        try:
            cliente = self.request.user.cliente
            queryset = Reserva.objects.filter(cliente=cliente).order_by('-fecha_inicio')
            forma = FiltroReservaForm(self.request.GET)
            
            if forma.is_valid():
                marca_vehiculo = forma.cleaned_data.get('marca_vehiculo')
                estado = forma.cleaned_data.get('estado')
                fecha_inicio_desde = forma.cleaned_data.get('fecha_inicio_desde')
                fecha_inicio_hasta = forma.cleaned_data.get('fecha_inicio_hasta')
                
                if marca_vehiculo:
                    queryset = queryset.filter(vehiculo__marca__icontains=marca_vehiculo)
                if estado:
                    queryset = queryset.filter(estado=estado)
                if fecha_inicio_desde:
                    queryset = queryset.filter(fecha_inicio__gte=fecha_inicio_desde)
                if fecha_inicio_hasta:
                    queryset = queryset.filter(fecha_inicio__lte=fecha_inicio_hasta)
            
            return queryset
        except Cliente.DoesNotExist:
            return Reserva.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['cliente'] = self.request.user.cliente
        except Cliente.DoesNotExist:
            context['cliente'] = None
        context['form'] = FiltroReservaForm(self.request.GET)
        return context


class ClienteReservaDetailView(LoginRequiredMixin, DetailView):
    """Detalle de una reserva del cliente"""
    model = Reserva
    template_name = 'cliente_panel/reserva_detail.html'
    context_object_name = 'reserva'
    login_url = 'login'

    def get_queryset(self):
        try:
            cliente = self.request.user.cliente
            return Reserva.objects.filter(cliente=cliente)
        except Cliente.DoesNotExist:
            return Reserva.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['cliente'] = self.request.user.cliente
        except Cliente.DoesNotExist:
            context['cliente'] = None
        return context


class ClienteMisFacturasListView(LoginRequiredMixin, ListView):
    """Lista de facturas del cliente autenticado"""
    model = Factura
    template_name = 'cliente_panel/mis_facturas.html'
    context_object_name = 'facturas'
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        # Verificar que sea cliente, no admin
        if request.user.is_staff or request.user.is_superuser:
            return redirect('panel_admin')
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        try:
            cliente = self.request.user.cliente
            # Obtener facturas de las reservas del cliente
            reservas_cliente = Reserva.objects.filter(cliente=cliente)
            queryset = Factura.objects.filter(reserva__in=reservas_cliente).order_by('-fecha_emision')
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
            
            return queryset
        except Cliente.DoesNotExist:
            return Factura.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['cliente'] = self.request.user.cliente
        except Cliente.DoesNotExist:
            context['cliente'] = None
        context['form'] = FiltroFacturaForm(self.request.GET)
        return context


class ClienteFacturaDetailView(LoginRequiredMixin, DetailView):
    """Detalle de una factura del cliente"""
    model = Factura
    template_name = 'cliente_panel/factura_detail.html'
    context_object_name = 'factura'
    login_url = 'login'

    def get_queryset(self):
        try:
            cliente = self.request.user.cliente
            reservas_cliente = Reserva.objects.filter(cliente=cliente)
            return Factura.objects.filter(reserva__in=reservas_cliente)
        except Cliente.DoesNotExist:
            return Factura.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['cliente'] = self.request.user.cliente
        except Cliente.DoesNotExist:
            context['cliente'] = None
        return context


class ClienteMisDevolucionesListView(LoginRequiredMixin, ListView):
    """Lista de devoluciones del cliente autenticado"""
    model = Devolucion
    template_name = 'cliente_panel/mis_devoluciones.html'
    context_object_name = 'devoluciones'
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        # Verificar que sea cliente, no admin
        if request.user.is_staff or request.user.is_superuser:
            return redirect('panel_admin')
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        try:
            cliente = self.request.user.cliente
            # Obtener devoluciones de las reservas del cliente
            reservas_cliente = Reserva.objects.filter(cliente=cliente)
            queryset = Devolucion.objects.filter(reserva__in=reservas_cliente).order_by('-fecha_devolucion')
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
            
            return queryset
        except Cliente.DoesNotExist:
            return Devolucion.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['cliente'] = self.request.user.cliente
        except Cliente.DoesNotExist:
            context['cliente'] = None
        context['form'] = FiltroDevolucionForm(self.request.GET)
        return context


class ClienteDevolucionDetailView(LoginRequiredMixin, DetailView):
    """Detalle de una devolución del cliente"""
    model = Devolucion
    template_name = 'cliente_panel/devolucion_detail.html'
    context_object_name = 'devolucion'
    login_url = 'login'

    def get_queryset(self):
        try:
            cliente = self.request.user.cliente
            reservas_cliente = Reserva.objects.filter(cliente=cliente)
            return Devolucion.objects.filter(reserva__in=reservas_cliente)
        except Cliente.DoesNotExist:
            return Devolucion.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['cliente'] = self.request.user.cliente
        except Cliente.DoesNotExist:
            context['cliente'] = None
        return context


class ClienteMiPerfilView(LoginRequiredMixin, UpdateView):
    """Ver y editar perfil del cliente autenticado"""
    model = Cliente
    form_class = ClientePerfilForm
    template_name = 'cliente_panel/mi_perfil.html'
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        # Verificar que sea cliente, no admin
        if request.user.is_staff or request.user.is_superuser:
            return redirect('panel_admin')
        return super().get(request, *args, **kwargs)

    def get_object(self):
        try:
            return self.request.user.cliente
        except Cliente.DoesNotExist:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cliente = self.get_object()
        context['cliente'] = cliente
        
        # Pasar el formulario con datos iniciales
        if 'form' not in kwargs:
            context['form'] = self.get_form()
            if cliente and cliente.user:
                context['form'].fields['email'].initial = cliente.user.email
        
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Tu perfil ha sido actualizado exitosamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('cliente_mi_perfil')


class ClienteReservaEditView(LoginRequiredMixin, UpdateView):
    """Editar reserva propia del cliente (solo si está pendiente)"""
    model = Reserva
    form_class = ClienteReservaForm
    template_name = 'cliente_panel/editar_reserva.html'
    login_url = 'login'
    
    def get_queryset(self):
        try:
            cliente = self.request.user.cliente
            # Solo permitir editar reservas pendientes
            return Reserva.objects.filter(cliente=cliente, estado='pendiente')
        except Cliente.DoesNotExist:
            return Reserva.objects.none()
    
    def form_valid(self, form):
        reserva = form.save(commit=False)
        
        # Recalcular total
        if reserva.fecha_inicio and reserva.fecha_fin and reserva.vehiculo:
            dias = (reserva.fecha_fin - reserva.fecha_inicio).days + 1
            reserva.total = reserva.vehiculo.costo_dia * dias
        
        reserva.save()
        messages.success(self.request, 'Reserva actualizada exitosamente.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('cliente_mis_reservas')


class ClienteReservaCancelarView(LoginRequiredMixin, DeleteView):
    """Cancelar reserva propia del cliente (solo si está pendiente)"""
    model = Reserva
    template_name = 'cliente_panel/confirmar_cancelar_reserva.html'
    login_url = 'login'
    
    def get_queryset(self):
        try:
            cliente = self.request.user.cliente
            # Solo permitir cancelar reservas pendientes o confirmadas
            return Reserva.objects.filter(cliente=cliente, estado__in=['pendiente', 'confirmada'])
        except Cliente.DoesNotExist:
            return Reserva.objects.none()
    
    def delete(self, request, *args, **kwargs):
        reserva = self.get_object()
        vehiculo = reserva.vehiculo
        
        # Cambiar estado a cancelada en lugar de eliminar
        reserva.estado = 'cancelada'
        reserva.save()
        
        # Verificar si hay otras reservas activas
        reservas_activas = Reserva.objects.filter(
            vehiculo=vehiculo,
            estado__in=['pendiente', 'confirmada']
        ).exclude(pk=reserva.pk).exists()
        
        # Si no hay otras reservas activas, marcar vehículo como disponible
        if not reservas_activas:
            vehiculo.disponible = True
            vehiculo.save()
        
        messages.success(request, 'Reserva cancelada exitosamente.')
        return redirect('cliente_mis_reservas')


class ClienteDevolucionCreateView(LoginRequiredMixin, CreateView):
    """Crear una devolución de una reserva completada"""
    model = Devolucion
    form_class = ClienteDevolucionForm
    template_name = 'cliente_panel/crear_devolucion.html'
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        # Obtener la reserva del URL
        self.reserva = get_object_or_404(Reserva, pk=kwargs.get('reserva_pk'))
        
        # Verificar que la reserva pertenezca al cliente
        try:
            cliente = request.user.cliente
            if self.reserva.cliente != cliente:
                return redirect('panel_cliente')
        except Cliente.DoesNotExist:
            return redirect('login')
        
        # Verificar que la reserva esté confirmada
        if self.reserva.estado != 'confirmada':
            messages.error(request, 'Solo puedes registrar devolución para reservas confirmadas.')
            return redirect('cliente_mis_reservas')
        
        # Verificar que NO exista devolución previa
        if hasattr(self.reserva, 'devolucion'):
            messages.warning(request, 'Esta reserva ya tiene una devolución registrada.')
            return redirect('cliente_devolucion_detail', pk=self.reserva.devolucion.pk)
        
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Obtener la reserva del URL
        self.reserva = get_object_or_404(Reserva, pk=kwargs.get('reserva_pk'))
        
        # Verificar que la reserva pertenezca al cliente
        try:
            cliente = request.user.cliente
            if self.reserva.cliente != cliente:
                return redirect('panel_cliente')
        except Cliente.DoesNotExist:
            return redirect('login')
        
        # Verificar que NO exista devolución previa
        if hasattr(self.reserva, 'devolucion'):
            messages.error(request, 'Esta reserva ya tiene una devolución registrada.')
            return redirect('cliente_devolucion_detail', pk=self.reserva.devolucion.pk)
        
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reserva'] = self.reserva
        return context

    def form_valid(self, form):
        # Verificar una última vez que NO exista devolución
        try:
            devolucion_existente = self.reserva.devolucion
            messages.error(self.request, 'Esta reserva ya tiene una devolución registrada.')
            return redirect('cliente_devolucion_detail', pk=devolucion_existente.pk)
        except Devolucion.DoesNotExist:
            pass
        
        devolucion = form.save(commit=False)
        devolucion.reserva = self.reserva
        
        # Calcular penalización automáticamente
        penalizacion = devolucion.calcular_penalizacion()
        devolucion.save()
        
        # Actualizar factura con penalización
        devolucion.actualizar_factura_con_penalizacion()
        
        # Marcar vehículo como disponible nuevamente
        devolucion.reserva.vehiculo.disponible = True
        devolucion.reserva.vehiculo.save()
        
        messages.success(self.request, f'Devolución registrada. Penalización: ${devolucion.penalizacion:,.2f}')
        
        # Retornar la redirección al URL de éxito sin llamar a super()
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('cliente_mis_devoluciones')

