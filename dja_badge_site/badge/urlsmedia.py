from django.urls import path

from .views import viewsmedia

urlpatterns = [
    path('metadato/<int:metadato_id>/<str:file_name>', viewsmedia.metadato, name='metadato_file'),
    path('file_sfondo/<int:modello_id>/<str:file_name>', viewsmedia.sfondo_file, name='sfondo_file'),
]