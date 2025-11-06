from django.db import models
from django.contrib.auth.models import User
import uuid

class VCard(models.Model):
    # Genera un UUID univoco per ogni contatto
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Altri campi
    #user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='contatto')
    organizzazione = models.CharField(max_length=100, default="Comune di Bari")
    titolo = models.CharField(max_length=10, blank=True, null=True)
    nome = models.CharField(max_length=100)
    cognome = models.CharField(max_length=100)
    profilo = models.CharField(max_length=100)
    ufficio = models.CharField(max_length=150)
    indirizzo_ufficio = models.CharField(max_length=255)
    telefono_fisso = models.CharField(max_length=20, blank=True, null=True)
    telefono_cellulare = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    effetto_neve = models.BooleanField()
    effetto_epifania = models.BooleanField()

    def __str__(self):
        return f'{self.cognome} {self.nome}'
    
    def save_model(self, request, obj, form, change):
        if not obj.user:
            obj.user = request.user
        super().save_model(request, obj, form, change)

