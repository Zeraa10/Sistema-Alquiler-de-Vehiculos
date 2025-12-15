# Generated migration for authentication refactoring

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


def create_users_for_clients(apps, schema_editor):
    """Crear usuarios para clientes que no tengan uno"""
    Cliente = apps.get_model('core', 'Cliente')
    User = apps.get_model('auth', 'User')
    
    for cliente in Cliente.objects.filter(user__isnull=True):
        # Crear un usuario con email genérico basado en el nombre
        username = f"{cliente.nombre.lower()}{cliente.id}".replace(" ", "")
        email = f"{username}@alquizera.local"
        
        # Evitar duplicados
        counter = 1
        original_username = username
        while User.objects.filter(username=username).exists():
            username = f"{original_username}{counter}"
            counter += 1
        
        # Crear usuario
        user = User.objects.create_user(username=username, email=email)
        cliente.user = user
        cliente.save()


def reverse_create_users(apps, schema_editor):
    """Revertir - eliminar usuarios creados automáticamente"""
    Cliente = apps.get_model('core', 'Cliente')
    User = apps.get_model('auth', 'User')
    
    # Eliminar usuarios creados automáticamente
    clientes = Cliente.objects.filter(user__isnull=False)
    user_ids = clientes.values_list('user_id', flat=True)
    User.objects.filter(id__in=user_ids, email__endswith='@alquizera.local').delete()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0004_vehiculo_imagen'),
    ]

    operations = [
        # Remove old fields correo and contrasena
        migrations.RemoveField(
            model_name='cliente',
            name='correo',
        ),
        migrations.RemoveField(
            model_name='cliente',
            name='contrasena',
        ),
        # Add new field user (nullable initially)
        migrations.AddField(
            model_name='cliente',
            name='user',
            field=models.OneToOneField(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='cliente', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        # Data migration to create users for existing clients
        migrations.RunPython(create_users_for_clients, reverse_create_users),
        # Make user field non-nullable after data migration
        migrations.AlterField(
            model_name='cliente',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='cliente', to=settings.AUTH_USER_MODEL),
        ),
    ]
