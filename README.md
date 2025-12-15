# ALQUIZERA – Sistema de Alquiler de Vehículos

ALQUIZERA es una aplicación web para gestionar el alquiler de vehículos, desarrollada con Django y PostgreSQL, que ofrece paneles separados para clientes y administradores, reservas en línea y gestión completa del inventario de vehículos.

## **Características principales**
**-Autenticación y roles**

-Registro e inicio de sesión de clientes.

-Panel de cliente y panel de administración separados.

-Administrador creado desde la consola (no se registra vía web).

**-Panel de cliente**

-Ver vehículos disponibles.

-Crear nuevas reservas.

-Consultar y cancelar reservas propias (según estado).

-Ver facturas y devoluciones asociadas.

-Actualizar datos de perfil.

**-Panel de administración**

-Gestión de clientes.

-Gestión de vehículos (incluye estado de disponibilidad e imagen).

-Gestión de reservas y devoluciones.

-Gestión de facturas.

-Gestión de categorías y subcategorías de licencia de conducir.

**-Landing page**

-Página de inicio pública con información de ALQUIZERA.

-Enlaces directos para ver vehículos, iniciar sesión y registrarse.

## **Tecnologías utilizadas**
**-Backend:** Django (Python)

**-Base de datos:** PostgreSQL

**-Frontend:** HTML5, CSS3 (estilos personalizados / Bootstrap ligero)

**-Otros:** Git, entorno virtual de Python (venv)

## **Requisitos previos**
-Python 3.10+

-PostgreSQL instalado y una base de datos creada (por ejemplo alquiler_vehiculos)

-Git

## **Instalación y configuración**
**1. Clonar el repositorio**

```
git clone https://github.com/Zeraa10/Sistema-Alquiler-de-Vehiculos.git
cd Sistema-Alquiler-de-Vehiculos
```
**2.Crear y activar un entorno virtual**

```
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate
```
**3. Instalar dependencias**

```
pip install -r requirements.txt
```
**4. Configurar variables de entorno**

Copia el archivo de ejemplo y ajusta tus credenciales:

```
cp .env.example .env
```
Edita .env con:
-Credenciales de PostgreSQL (nombre de base de datos, usuario, contraseña, host, puerto).

-Clave secreta de Django (SECRET_KEY).

-Otros parámetros necesarios (DEBUG, ALLOWED_HOSTS, etc.).

**5. Aplicar migraciones**
```
python manage.py migrate
```

**6. Crear superusuario (administrador)**
```
python manage.py createsuperuser
```

Sigue las instrucciones de la consola para crear el usuario admin.

**7. Cargar datos iniciales (opcional)**

Si tienes fixtures o scripts para categorías de licencia, puedes ejecutarlos aquí.
(Ejemplo: python manage.py loaddata licencias.json si se agrega más adelante.)

**8. Levantar el servidor de desarrollo**
```
python manage.py runserver
```
Abre en el navegador:

http://127.0.0.1:8000/ → Landing page (home de ALQUIZERA).

http://127.0.0.1:8000/admin/ → Admin de Django.

http://127.0.0.1:8000/login/ → Login de la aplicación.

http://127.0.0.1:8000/panel-cliente/ → Panel de cliente (tras autenticarse).

http://127.0.0.1:8000/panel-admin/ → Panel de administración (usuario admin).

## **Estructura del proyecto**

```
alquiler-vehiculos/
├─ alquiler/               # Configuración principal de Django (settings, urls, wsgi, asgi)
├─ core/                   # App principal de la aplicación
│  ├─ models.py            # Modelos: Cliente, Vehiculo, Reserva, Devolucion, Factura, Licencias...
│  ├─ forms.py             # Formularios basados en ModelForm
│  ├─ views.py             # Vistas generales
│  ├─ views/
│  │  ├─ auth_views.py             # Login, registro, logout y redirecciones por rol
│  │  ├─ home_views.py             # Landing page / Home
│  │  ├─ panel_views.py            # Panel admin / redirecciones
│  │  ├─ cliente_panel_views.py    # Vistas del panel de cliente
│  │  ├─ vehiculo_views.py         # CRUD de Vehiculo
│  │  ├─ reserva_views.py          # CRUD de Reserva
│  │  ├─ devolucion_views.py       # CRUD de Devolucion
│  │  ├─ factura_views.py          # CRUD de Factura
│  │  ├─ categoria_licencia_views.py
│  │  └─ subcategoria_licencia_views.py
│  ├─ urls.py              # Rutas de la app core
│  └─ migrations/          # Migraciones del modelo
├─ templates/              # Plantillas HTML
│  ├─ base.html
│  ├─ home.html
│  ├─ panel_cliente.html
│  ├─ panel_admin.html
│  ├─ auth/...
│  ├─ cliente_panel/...
│  ├─ vehiculo/...
│  ├─ reserva/...
│  ├─ devolucion/...
│  ├─ factura/...
│  └─ (resto de carpetas por módulo)
├─ requirements.txt
├─ manage.py
└─ .env.example
```

**Licencia**
Este proyecto se distribuye con fines educativos. Puedes adaptarlo y mejorarlo según tus necesidades. Añade aquí la licencia que prefieras (por ejemplo MIT) si decides formalizarla.

