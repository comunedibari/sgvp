from django.urls import path
from .views import vcard_by_id, generate_vcf
#from .views import viewspass,viewsmodello,viewsmetadatomodello,viewsserie,viewssottoserie,viewstest

urlpatterns = [
    path('<uuid:vcard_id>/', vcard_by_id, name='vcard_by_id'),
    path('<uuid:vcard_id>/generate_vcf/', generate_vcf, name='generate_vcf'),
]