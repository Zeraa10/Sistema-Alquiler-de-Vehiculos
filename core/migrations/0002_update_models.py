# Generated manually to sync models with database

import django.db.models.deletion
from django.db import migrations, models


def create_default_licencias(apps, schema_editor):
    """Crear categorías y subcategorías de licencia por defecto"""
    CategoriaLicencia = apps.get_model('core', 'CategoriaLicencia')
    SubcategoriaLicencia = apps.get_model('core', 'SubcategoriaLicencia')
    
    # Crear categorías básicas
    cat_a = CategoriaLicencia.objects.create(codigo='A', descripcion='Motocicletas')
    cat_b = CategoriaLicencia.objects.create(codigo='B', descripcion='Automóviles')
    cat_c = CategoriaLicencia.objects.create(codigo='C', descripcion='Camiones')
    
    # Crear subcategorías básicas
    SubcategoriaLicencia.objects.create(codigo='A1', descripcion='Motocicletas hasta 125cc', categoria=cat_a)
    SubcategoriaLicencia.objects.create(codigo='A2', descripcion='Motocicletas hasta 600cc', categoria=cat_a)
    SubcategoriaLicencia.objects.create(codigo='B1', descripcion='Automóviles particulares', categoria=cat_b)
    SubcategoriaLicencia.objects.create(codigo='B2', descripcion='Automóviles comerciales', categoria=cat_b)


def assign_default_licencia_to_clients(apps, schema_editor):
    """Asignar una subcategoría por defecto a los clientes existentes"""
    Cliente = apps.get_model('core', 'Cliente')
    SubcategoriaLicencia = apps.get_model('core', 'SubcategoriaLicencia')
    
    default_licencia = SubcategoriaLicencia.objects.first()
    if default_licencia:
        Cliente.objects.filter(licencia_fk__isnull=True).update(licencia_fk=default_licencia)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        # Crear CategoriaLicencia
        migrations.CreateModel(
            name='CategoriaLicencia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=1, unique=True)),
                ('descripcion', models.CharField(max_length=100)),
            ],
        ),
        # Crear SubcategoriaLicencia
        migrations.CreateModel(
            name='SubcategoriaLicencia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=3, unique=True)),
                ('descripcion', models.TextField()),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subcategorias', to='core.categorialicencia')),
            ],
        ),
        # Ejecutar función para crear licencias por defecto
        migrations.RunPython(create_default_licencias, reverse_code=migrations.RunPython.noop),
        # Modificar Vehiculo: agregar color y disponible, eliminar estado
        migrations.AddField(
            model_name='vehiculo',
            name='color',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='vehiculo',
            name='disponible',
            field=models.BooleanField(default=True),
        ),
        migrations.RemoveField(
            model_name='vehiculo',
            name='estado',
        ),
        # Modificar Cliente: agregar campos nuevos primero
        migrations.AddField(
            model_name='cliente',
            name='apellido',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cliente',
            name='correo',
            field=models.EmailField(default='temp@temp.com', max_length=254, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cliente',
            name='telefono',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='cliente',
            name='contrasena',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        # Agregar nuevo campo licencia_fk como ForeignKey (temporalmente nullable)
        migrations.AddField(
            model_name='cliente',
            name='licencia_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='clientes_temp', to='core.subcategorialicencia'),
        ),
        # Asignar una subcategoría por defecto a los clientes existentes
        migrations.RunPython(
            assign_default_licencia_to_clients,
            reverse_code=migrations.RunPython.noop
        ),
        # Eliminar campos antiguos de Cliente
        migrations.RemoveField(
            model_name='cliente',
            name='contacto',
        ),
        migrations.RemoveField(
            model_name='cliente',
            name='user',
        ),
        # Eliminar campo licencia antiguo (CharField)
        migrations.RemoveField(
            model_name='cliente',
            name='licencia',
        ),
        # Renombrar licencia_fk a licencia
        migrations.RenameField(
            model_name='cliente',
            old_name='licencia_fk',
            new_name='licencia',
        ),
        # Hacer licencia no nullable y cambiar related_name
        migrations.AlterField(
            model_name='cliente',
            name='licencia',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clientes', to='core.subcategorialicencia'),
        ),
        # Modificar nombre de Cliente para que tenga max_length=50
        migrations.AlterField(
            model_name='cliente',
            name='nombre',
            field=models.CharField(max_length=50),
        ),
        # Crear Devolucion
        migrations.CreateModel(
            name='Devolucion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_devolucion', models.DateField()),
                ('estado_devolucion', models.CharField(choices=[('entregado', 'Entregado'), ('atrasado', 'Atrasado'), ('danado', 'Dañado')], max_length=20)),
                ('penalizacion', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('reserva', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='devolucion', to='core.reserva')),
            ],
        ),
        # Modificar Reserva: eliminar fecha_devolucion (ahora está en Devolucion)
        migrations.RemoveField(
            model_name='reserva',
            name='fecha_devolucion',
        ),
        # Modificar Reserva: cambiar on_delete de PROTECT a CASCADE
        migrations.AlterField(
            model_name='reserva',
            name='cliente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservas', to='core.cliente'),
        ),
        migrations.AlterField(
            model_name='reserva',
            name='vehiculo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservas', to='core.vehiculo'),
        ),
        # Modificar Factura: agregar unique=True a numero
        migrations.AlterField(
            model_name='factura',
            name='numero',
            field=models.CharField(max_length=30, unique=True),
        ),
    ]


