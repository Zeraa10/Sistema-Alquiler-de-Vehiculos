# Generated manually to add imagen field to Vehiculo

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_factura_reserva_alter_reserva_estado'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehiculo',
            name='imagen',
            field=models.ImageField(blank=True, help_text='Imagen del vehículo', null=True, upload_to='vehiculos/'),
        ),
    ]


