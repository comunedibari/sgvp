from django.contrib import admin
from django.contrib.admin import display
from django.urls import path
from django.contrib.auth.admin import UserAdmin,GroupAdmin
from django.contrib.auth.models import User,Group
from django.contrib.auth.models import Group

from .views import viewspass


from .models import ApiKey, Serie, UserSeries
from .models import SottoSerie
from .models import ModelloStampaBadge
from .models import MetadatoModelloBadge
from .models import Badge
from .models import MetadatoBadge
from vcard.models import VCard

from csvexport.actions import csvexport



class CustomAdminSite(admin.AdminSite):
    """Estensione del default admin site per aggiungere tra le url 
    gestite anche la url per permettere la preview del badge a partire dal metadato

    Args:
        admin (_type_): _description_
    """
    def get_urls(self):
        urls = super(CustomAdminSite, self).get_urls()
        custom_urls = [
            path(r'badge/modello_stampa_preview/<int:modello_id>', self.admin_view(viewspass.badge_preview), name="badge_preview"),
        ]
        return  custom_urls + urls 
    site_title = 'Verifica Pass - Backoffice'

    # Text to put in each page's <h1> (and above login form).
    site_header = 'Backoffice'

    # Text to put at the top of the admin index page.
    index_title = 'Verifica Pass'
    
admin_site = CustomAdminSite(name="admin")

#reinserisco utenti e gruppi che con la customizzazione del sito non venivano più mostrati
admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)

# Register your models here.
class ModelloStampaBadgeAdmin(admin.ModelAdmin):
    list_display = ('nome_template', 'file_sfondo', 'width', 'height')
    change_form_template = 'admin/badge_edit_template.html'

#admin_site.register(ModelloStampaBadge, ModelloStampaBadgeAdmin)

class SerieAdmin(admin.ModelAdmin):
    list_display = ('nome', 'sigla','progr_emissione', 'data_inizio_validita', 'data_fine_validita')
    readonly_fields= ['progr_emissione']
    
    # per definire i campi readonly in caso di creazione o variazione
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["progr_emissione", "sigla"]
        else:
            return ["progr_emissione"]

#admin_site.register(Serie,SerieAdmin)

class SottoSerieAdmin(admin.ModelAdmin):
    list_display = ('nome', 'data_inizio_validita', 'data_fine_validita')
    
#admin_site.register(SottoSerie,SottoSerieAdmin)

class MetadatoModelloBadgeAdmin(admin.ModelAdmin):
    list_display = ('modello_stampa_badge', 'nome', 'tipo_metadato', 'stampabile')

#admin_site.register(MetadatoModelloBadge,MetadatoModelloBadgeAdmin)

class MetadatoBadgeInline(admin.StackedInline):
    model = MetadatoBadge
    extra = 0

class BadgeAdmin(admin.ModelAdmin):
    
    @display(description='Serie')
    def serie_val(admin,self) -> str:
        return str(self.sotto_serie.serie)
    list_display = ('codice', 'serie_val', 'sotto_serie', 'descrizione','data_inizio_validita', 'data_fine_validita')
    readonly_fields= ['codice']
    list_filter = ('codice','sotto_serie',)
    inlines = [MetadatoBadgeInline]
    actions = [csvexport]
    

#admin_site.register(Badge,BadgeAdmin)

class MetadatoBadgeAdmin(admin.ModelAdmin):
    list_display = ('__str__','valore')
    
    def valore(admin,self):
        valore_ritorno=self.valore_testo
        if self.metadato.tipo_metadato in (MetadatoModelloBadge.TP_DATE):
            valore_ritorno=self.valore_data
        elif self.metadato.tipo_metadato in (MetadatoModelloBadge.TP_IMAGE):
            valore_ritorno=self.valore_image
        elif self.metadato.tipo_metadato in (MetadatoModelloBadge.TP_FILE):    
            valore_ritorno=self.valore_file
        return valore_ritorno
    
    #customizzazione form in modo da renderizzare il campo valore_XXXX secondo il tipo_metadato
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            field_dinamici=['valore_testo','valore_image','valore_file','valore_data']
            if obj.metadato.tipo_metadato in (MetadatoModelloBadge.TP_DATE,):
                field_dinamici.remove('valore_data')
            elif obj.metadato.tipo_metadato in (MetadatoModelloBadge.TP_FILE,):
                field_dinamici.remove('valore_file')
            elif obj.metadato.tipo_metadato in (MetadatoModelloBadge.TP_IMAGE,):
                field_dinamici.remove('valore_image')
            else:
                field_dinamici.remove('valore_testo')
            for field_da_rimuovere in field_dinamici:
                if field_da_rimuovere in form.base_fields:
                    del form.base_fields[field_da_rimuovere]
        return form
    
#admin_site.register(MetadatoBadge,MetadatoBadgeAdmin)


class UserSeriesAdmin(admin.ModelAdmin):
    list_display = ('serie', 'user', 'ruolo', 'data_inizio_validita', 'data_fine_validita')
    list_filter = ('user','serie',)
    
admin_site.register(UserSeries,UserSeriesAdmin)


class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ('sotto_serie', 'key', 'data_inizio_validita', 'data_fine_validita')
    list_filter = ('sotto_serie',)
    
admin_site.register(ApiKey,ApiKeyAdmin)

# Creo sezione admin anche per app vcard
class VCardAdmin(admin.ModelAdmin):
    
    # Specifica i campi che vuoi visualizzare nella lista dell'amministratore
    list_display = ('nome', 'cognome', 'profilo', 'ufficio', 'telefono_fisso', 'telefono_cellulare', 'email')
    
    # Aggiungi un filtro per i campi più usati
    list_filter = ('profilo', 'ufficio')
    
    # Aggiungi un'opzione di ricerca basata su nome e cognome
    search_fields = ('nome', 'cognome', 'profilo', 'ufficio', 'email')
    
    # Permetti di filtrare e modificare i contatti per indirizzo
    ordering = ('cognome', 'nome')

    # Definisci una formattazione personalizzata per il dettaglio
    fieldsets = (
        (None, {
            'fields': ('uuid', 'titolo', 'nome', 'cognome', 'profilo', 'ufficio', 'indirizzo_ufficio')
        }),
        ('Contatti', {
            'fields': ('telefono_fisso', 'telefono_cellulare', 'email')
        }),
        ('Altro', {
            'fields': ('effetto_neve', 'effetto_epifania')
        }),
    )

    readonly_fields = ('uuid',)

    # Aggiungi un'opzione per il numero massimo di elementi per pagina
    list_per_page = 20

admin_site.register(VCard, VCardAdmin)
