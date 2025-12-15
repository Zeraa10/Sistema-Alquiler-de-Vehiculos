from django.urls import path
from core.views.home_views import HomeView
from core.views.panel_views import PanelClienteView, PanelAdminView
from core.views.categoria_licencia_views import (
    CategoriaLicenciaList, CategoriaLicenciaDetail, CategoriaLicenciaCreate,
    CategoriaLicenciaUpdate, CategoriaLicenciaDelete
)
from core.views.subcategoria_licencia_views import (
    SubcategoriaLicenciaList, SubcategoriaLicenciaDetail, SubcategoriaLicenciaCreate,
    SubcategoriaLicenciaUpdate, SubcategoriaLicenciaDelete
)
from core.views.cliente_views import (
    ClienteList, ClienteDetail, ClienteCreate, ClienteUpdate, ClienteDelete
)
from core.views.vehiculo_views import (
    VehiculoList, VehiculoDetail, VehiculoCreate, VehiculoUpdate, VehiculoDelete
)
from core.views.reserva_views import (
    ReservaList, ReservaDetail, ReservaCreate, ReservaUpdate, ReservaDelete
)
from core.views.devolucion_views import (
    DevolucionList, DevolucionDetail, DevolucionCreate, DevolucionUpdate, DevolucionDelete
)
from core.views.factura_views import (
    FacturaList, FacturaDetail, FacturaCreate, FacturaUpdate, FacturaDelete
)
from core.views.auth_views import LoginView, LogoutView, RegisterView
from core.views.cliente_panel_views import (
    ClienteVehiculosListView,
    ClienteNuevaReservaView,
    ClienteMisReservasListView,
    ClienteReservaDetailView,
    ClienteMisFacturasListView,
    ClienteFacturaDetailView,
    ClienteMisDevolucionesListView,
    ClienteDevolucionDetailView,
    ClienteMiPerfilView,
    ClienteReservaEditView,
    ClienteReservaCancelarView,
    ClienteDevolucionCreateView,
)

urlpatterns = [
    # Home
    path('', HomeView.as_view(), name='home'),

    # Paneles
    path('panel-cliente/', PanelClienteView.as_view(), name='panel_cliente'),
    path('panel-admin/', PanelAdminView.as_view(), name='panel_admin'),

    # Panel de Cliente - Vistas específicas
    path('cliente/vehiculos/', ClienteVehiculosListView.as_view(), name='cliente_vehiculos'),
    path('cliente/nueva-reserva/', ClienteNuevaReservaView.as_view(), name='cliente_nueva_reserva'),
    path('cliente/mis-reservas/', ClienteMisReservasListView.as_view(), name='cliente_mis_reservas'),
    path('cliente/reserva/<int:pk>/', ClienteReservaDetailView.as_view(), name='cliente_reserva_detail'),
    path('cliente/reserva/<int:pk>/editar/', ClienteReservaEditView.as_view(), name='cliente_reserva_edit'),
    path('cliente/reserva/<int:pk>/cancelar/', ClienteReservaCancelarView.as_view(), name='cliente_reserva_cancelar'),
    path('cliente/mis-facturas/', ClienteMisFacturasListView.as_view(), name='cliente_mis_facturas'),
    path('cliente/factura/<int:pk>/', ClienteFacturaDetailView.as_view(), name='cliente_factura_detail'),
    path('cliente/mis-devoluciones/', ClienteMisDevolucionesListView.as_view(), name='cliente_mis_devoluciones'),
    path('cliente/devolucion/<int:pk>/', ClienteDevolucionDetailView.as_view(), name='cliente_devolucion_detail'),
    path('cliente/reserva/<int:reserva_pk>/devolucion/nueva/', ClienteDevolucionCreateView.as_view(), name='cliente_devolucion_create'),
    path('cliente/mi-perfil/', ClienteMiPerfilView.as_view(), name='cliente_mi_perfil'),

    # Categoría Licencia
    path('categoria_licencia/', CategoriaLicenciaList.as_view(), name='categoria_licencia_list'),
    path('categoria_licencia/<int:pk>/', CategoriaLicenciaDetail.as_view(), name='categoria_licencia_detail'),
    path('categoria_licencia/nuevo/', CategoriaLicenciaCreate.as_view(), name='categoria_licencia_create'),
    path('categoria_licencia/<int:pk>/editar/', CategoriaLicenciaUpdate.as_view(), name='categoria_licencia_update'),
    path('categoria_licencia/<int:pk>/eliminar/', CategoriaLicenciaDelete.as_view(), name='categoria_licencia_delete'),

    # Subcategoría Licencia
    path('subcategoria_licencia/', SubcategoriaLicenciaList.as_view(), name='subcategoria_licencia_list'),
    path('subcategoria_licencia/<int:pk>/', SubcategoriaLicenciaDetail.as_view(), name='subcategoria_licencia_detail'),
    path('subcategoria_licencia/nuevo/', SubcategoriaLicenciaCreate.as_view(), name='subcategoria_licencia_create'),
    path('subcategoria_licencia/<int:pk>/editar/', SubcategoriaLicenciaUpdate.as_view(), name='subcategoria_licencia_update'),
    path('subcategoria_licencia/<int:pk>/eliminar/', SubcategoriaLicenciaDelete.as_view(), name='subcategoria_licencia_delete'),

    # Cliente
    path('cliente/', ClienteList.as_view(), name='cliente_list'),
    path('cliente/<int:pk>/', ClienteDetail.as_view(), name='cliente_detail'),
    path('cliente/nuevo/', ClienteCreate.as_view(), name='cliente_create'),
    path('cliente/<int:pk>/editar/', ClienteUpdate.as_view(), name='cliente_update'),
    path('cliente/<int:pk>/eliminar/', ClienteDelete.as_view(), name='cliente_delete'),

    # Vehículo
    path('vehiculo/', VehiculoList.as_view(), name='vehiculo_list'),
    path('vehiculo/<int:pk>/', VehiculoDetail.as_view(), name='vehiculo_detail'),
    path('vehiculo/nuevo/', VehiculoCreate.as_view(), name='vehiculo_create'),
    path('vehiculo/<int:pk>/editar/', VehiculoUpdate.as_view(), name='vehiculo_update'),
    path('vehiculo/<int:pk>/eliminar/', VehiculoDelete.as_view(), name='vehiculo_delete'),

    # Reserva
    path('reserva/', ReservaList.as_view(), name='reserva_list'),
    path('reserva/<int:pk>/', ReservaDetail.as_view(), name='reserva_detail'),
    path('reserva/nuevo/', ReservaCreate.as_view(), name='reserva_create'),
    path('reserva/<int:pk>/editar/', ReservaUpdate.as_view(), name='reserva_update'),
    path('reserva/<int:pk>/eliminar/', ReservaDelete.as_view(), name='reserva_delete'),

    # Devolución
    path('devolucion/', DevolucionList.as_view(), name='devolucion_list'),
    path('devolucion/<int:pk>/', DevolucionDetail.as_view(), name='devolucion_detail'),
    path('devolucion/nuevo/', DevolucionCreate.as_view(), name='devolucion_create'),
    path('devolucion/<int:pk>/editar/', DevolucionUpdate.as_view(), name='devolucion_update'),
    path('devolucion/<int:pk>/eliminar/', DevolucionDelete.as_view(), name='devolucion_delete'),

    # Factura
    path('factura/', FacturaList.as_view(), name='factura_list'),
    path('factura/<int:pk>/', FacturaDetail.as_view(), name='factura_detail'),
    path('factura/nuevo/', FacturaCreate.as_view(), name='factura_create'),
    path('factura/<int:pk>/editar/', FacturaUpdate.as_view(), name='factura_update'),
    path('factura/<int:pk>/eliminar/', FacturaDelete.as_view(), name='factura_delete'),

    # Autenticación
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
]
