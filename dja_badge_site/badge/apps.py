from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig


class BadgeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'badge'
    verbose_name = 'Gestione Pass'

