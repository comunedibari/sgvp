# Generated by Django 4.1.7 on 2023-03-24 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('badge', '0012_metadatomodellobadge_tipo_pvc_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='metadatomodellobadge',
            name='tipo_pvc',
            field=models.CharField(choices=[('GENERICO', 'Generico'), ('COMUNE', 'Personale comune (art. 6)'), ('PARTICOLARE', 'Personale particolare (art. 9)')], default='GENERICO', max_length=12, verbose_name='Tipologia dato privacy'),
        ),
    ]
