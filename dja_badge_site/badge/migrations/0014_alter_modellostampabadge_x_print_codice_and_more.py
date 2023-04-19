# Generated by Django 4.1.7 on 2023-03-27 06:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('badge', '0013_alter_metadatomodellobadge_tipo_pvc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modellostampabadge',
            name='x_print_codice',
            field=models.DecimalField(blank=True, decimal_places=2, default=35, help_text='coordinata bottom left origin x in mm dove stampare il codice Pass', max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name='modellostampabadge',
            name='y_print_codice',
            field=models.DecimalField(blank=True, decimal_places=2, default=98, help_text='coordinata bottom left origin y in mm dove stampare il codice Pass', max_digits=5, null=True),
        ),
    ]