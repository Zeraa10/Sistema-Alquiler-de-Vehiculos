# INSTRUCCIONES POST-ACTUALIZACIÓN

## 🔄 PASOS NECESARIOS DESPUÉS DE ACTUALIZAR EL CÓDIGO

### 1. Activar el Entorno Virtual
```bash
# En Windows
.\venv\Scripts\activate

# En macOS/Linux
source venv/bin/activate
```

### 2. Instalar Dependencias Nuevas
```bash
pip install python-decouple
```

### 3. Configurar Variables de Entorno
```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar el archivo .env con tus valores
# IMPORTANTE: Cambiar credenciales de BD según tu configuración
```

### 4. Ejecutar Migraciones
```bash
python manage.py migrate
```

**NOTA IMPORTANTE:** 
Si tienes clientes existentes en la base de datos, la migración `0005_refactor_auth.py` puede fallar porque:
- Los antiguos clientes tienen `correo` y `contrasena` 
- Los nuevos clientes necesitan un `user` (FK a User)

#### Si tienes clientes existentes, sigue estos pasos adicionales:

```bash
# 1. Crear una migración de datos manual
python manage.py makemigrations

# 2. Abrir una shell Django
python manage.py shell

# 3. En la shell, ejecutar:
from django.contrib.auth.models import User
from core.models import Cliente

for cliente in Cliente.objects.filter(user__isnull=True):
    # Crear usuario Django para cada cliente
    user = User.objects.create_user(
        username=cliente.correo,  # Usar correo como username
        email=cliente.correo,
        password='temporal123'  # Contraseña temporal
    )
    cliente.user = user
    cliente.save()
    print(f"Cliente {cliente.nombre} vinculado a User {user.username}")

# 4. Salir de la shell (Ctrl+D o exit())
```

### 5. Crear Super Usuario (si es necesario)
```bash
python manage.py createsuperuser
# Ingresar email, username y contraseña
```

### 6. Recolectar Archivos Estáticos (para producción)
```bash
python manage.py collectstatic --noinput
```

### 7. Ejecutar Servidor de Desarrollo
```bash
python manage.py runserver
```

---

## 🔐 CONFIGURACIÓN DE VARIABLES DE ENTORNO

Archivo `.env` debe contener:

```ini
# Django
DEBUG=True
SECRET_KEY=tu-clave-secreta-aqui

# Base de Datos
DB_ENGINE=django.db.backends.postgresql
DB_NAME=alquiler_vehiculos
DB_USER=postgres
DB_PASSWORD=tu-contraseña-aqui
DB_HOST=localhost
DB_PORT=5432

# Email (opcional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-contraseña-app-aqui
```

### Cambios Importantes:
- **DEBUG=False** en producción
- **SECRET_KEY** debe ser única y segura
- **DB_PASSWORD** debe ser tu contraseña PostgreSQL

---

## ✅ VERIFICAR QUE TODO FUNCIONA

### 1. Login como Admin
- URL: http://127.0.0.1:8000/login/
- Usuario: tu email de admin
- Las vistas admin ahora requieren permisos

### 2. Login como Cliente
- URL: http://127.0.0.1:8000/login/
- Usuario: email de cualquier cliente
- Panel de cliente disponible en http://127.0.0.1:8000/panel-cliente/

### 3. Probar Funcionalidades Nuevas
- ✅ Crear reserva (auto-calcula total)
- ✅ Confirmar reserva (crea factura automáticamente)
- ✅ Editar reserva (cliente)
- ✅ Cancelar reserva (cliente)
- ✅ Registrar devolución (calcula penalización automáticamente)

---

## 🐛 TROUBLESHOOTING

### Error: "ModuleNotFoundError: No module named 'decouple'"
**Solución:**
```bash
pip install python-decouple
```

### Error: "no such table: core_cliente"
**Solución:**
```bash
python manage.py migrate
```

### Error: "duplicate key value violates unique constraint"
**Causa:** Clientes existentes sin User
**Solución:** Ver sección "Si tienes clientes existentes" arriba

### Error: Campo 'correo' no encontrado
**Causa:** La migración se ejecutó parcialmente
**Solución:** 
```bash
python manage.py migrate --fake core 0004_vehiculo_imagen
python manage.py migrate core
```

---

## 📋 CHECKLIST DE IMPLEMENTACIÓN

- [ ] Activar entorno virtual
- [ ] Instalar python-decouple
- [ ] Crear archivo .env
- [ ] Ejecutar migraciones
- [ ] Crear/actualizar super usuario
- [ ] Probar login admin
- [ ] Probar login cliente
- [ ] Probar crear reserva
- [ ] Probar editar reserva
- [ ] Probar cancelar reserva
- [ ] Probar crear factura
- [ ] Probar crear devolución

---

**Última actualización:** 2 de diciembre de 2025

Si encuentras problemas, revisa el archivo `MEJORAS_IMPLEMENTADAS.md` para más detalles.
