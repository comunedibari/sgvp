# Generated by Django 4.1.7 on 2023-03-13 13:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('badge', '0007_userseries'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userseries',
            name='serie',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_series', to='badge.serie'),
        ),
    ]
