from django import forms
import logging
from bootstrap_italia_template.widgets import BootstrapItaliaDateWidget

from .permission import user_sotto_series
from .models import Serie, SottoSerie,MetadatoBadge,MetadatoModelloBadge, UserSeries

logger = logging.getLogger(__name__)


class BadgeNewForm(forms.Form):
    """_summary_
        username argomento opzionale per filtrare le serie associate all'utente
    Args:
        forms (_type_): _description_
    """
    def __init__(self, *args, **kwargs):
        user=None
        if 'user' in kwargs:
            user=kwargs.pop('user')
        super().__init__(*args, **kwargs)
        if user:
            self.fields['sotto_serie'] = forms.ModelChoiceField(
                #queryset=SottoSerie.objects.filter(serie__user_series__user__username=username,serie__user_series__ruolo=UserSeries.TP_GESTORE),
                queryset=user_sotto_series(user=user,roles=[UserSeries.TP_GESTORE],valid_now=True),
                required=True,
                label="Tipo Pass")
    sotto_serie = forms.ModelChoiceField(queryset=SottoSerie.objects.all(),required=True,label="Tipo Pass")
    descrizione = forms.CharField(label='Descrizione Pass', max_length=80,required=True)
    data_inizio_validita = forms.DateField(label='Data inizio validità', required=True
                                           ,widget=BootstrapItaliaDateWidget())
    data_fine_validita = forms.DateField(label='Data fine validità', required=False
                                           ,widget=BootstrapItaliaDateWidget())

# si aspetta badgeObj in fase di costruzione
class BadgeEditForm(forms.Form):
    descrizione = forms.CharField(label='Descrizione Pass', max_length=80,required=True)
    data_inizio_validita = forms.DateField(label='Data inizio validità', required=True
                                           ,widget=BootstrapItaliaDateWidget())
    data_fine_validita = forms.DateField(label='Data fine validità', required=False
                                           ,widget=BootstrapItaliaDateWidget())
    #in construzione aggiungo i metadati già preesistenti 
    def __init__(self, *args, **kwargs):
        badgeObj=kwargs['badgeObj']
        kwargs.pop('badgeObj')
        super().__init__(*args, **kwargs)
        metadati = MetadatoBadge.objects.filter(badge_id=badgeObj.id)
        for metadato in metadati:
            field_name = 'metadato_'+str(metadato.id)
            if metadato.metadato.tipo_metadato==MetadatoModelloBadge.TP_DATE:
                self.fields[field_name] = forms.DateField(label=metadato.metadato.nome, required=metadato.metadato.obbligatorio
                                           ,widget=BootstrapItaliaDateWidget())
            elif metadato.metadato.tipo_metadato==MetadatoModelloBadge.TP_TEXT \
                or metadato.metadato.tipo_metadato==MetadatoModelloBadge.TP_HTML:
                self.fields[field_name] = forms.CharField(label=metadato.metadato.nome, 
                                                          required=metadato.metadato.obbligatorio,
                                                          widget=forms.Textarea(attrs={"rows":"1"}))        
            elif metadato.metadato.tipo_metadato==MetadatoModelloBadge.TP_STRING:    
                self.fields[field_name] = forms.CharField(label=metadato.metadato.nome, 
                                                          required=metadato.metadato.obbligatorio)        
                
class MetadatoBadgeForm(forms.ModelForm):
    class Meta:
        model = MetadatoBadge       
        fields = ['valore_image','valore_file']
    
