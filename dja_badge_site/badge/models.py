from datetime import date
import os
import uuid
from django import forms
from django.db import models
from django.contrib import admin
from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver
import logging
from .renameModel import RenameFilesModel
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

# Create your models here.
# Pass template

def get_file_entity_path(instance, filename):
    subpath='others'
    if isinstance(instance,ModelloStampaBadge):
        subpath='file_sfondo'
    elif isinstance(instance,MetadatoBadge):    
        subpath='metadato'
    return os.path.join(subpath, str(instance.id), filename)

# rappresenta il modello di stampa del Pass, contiene il file immagine di sfondo del Pass, le dimensioni in pixel e le coordinate dove va inserito il barcode
class ModelloStampaBadge(RenameFilesModel):
    RENAME_FILES = {'file_sfondo': {'dest': get_file_entity_path}}
    file_sfondo = models.ImageField(max_length=255,null=False,
                                    help_text="immagine di sfondo che determina le dimensioni del Pass in mm",upload_to="uploads/temp")
    nome_template = models.CharField(unique=True,max_length=100,null=False,help_text="nome univoco del template")
    x_px_qr=models.DecimalField(null=False,help_text="coordinata bottom left origin per il print del QRCODE in mm",default=34,verbose_name="x print QR (mm)",max_digits=5,decimal_places=2)
    y_px_qr=models.DecimalField(null=False,help_text="coordinata bottom left origin per il print del QRCODE in mm",default=33,verbose_name="y print QR (mm)",max_digits=5,decimal_places=2)
    version=models.IntegerField(null=False,help_text="version del QRCODE, default a 7 con ECC level al massimo arriva fino a 93 caratteri, attualmente url codificato è di 85 caratteri. Dettagli tecnici https://www.qrcode.com/en/about/version.html",default=7)
    box_size=models.IntegerField(null=False,help_text="dimensione del singolo box in pixel del QRCODE, (test effettuato con valore 2)",default=2)
    border=models.IntegerField(null=False,help_text="bordo del qrcode in unità di larghezza del singolo box, 'spec says border should be at least four boxes wide' (test effettuato con valore 3) ",default=3)
    width=models.DecimalField(null=True,blank=True,help_text="larghezza Pass in mm (105 per A6)",default=105,max_digits=5,decimal_places=2)
    height=models.DecimalField(null=True,blank=True,help_text="altezza Pass in mm (148 per A6)",default=148,max_digits=5,decimal_places=2)
    x_print_codice=models.DecimalField(null=True,blank=True,help_text="coordinata bottom left origin x in mm dove stampare il codice Pass",default=35,max_digits=5,decimal_places=2)
    y_print_codice=models.DecimalField(null=True,blank=True,help_text="coordinata bottom left origin y in mm dove stampare il codice Pass",default=98,max_digits=5,decimal_places=2)
    font_size_codice=models.IntegerField(null=True,blank=True,help_text="dimensione del font utilizzato per il codice, se vuoto verrà utilizzato 18 con font di tipo Courier",default=18)
    class Meta:
        verbose_name = 'Modello stampa pass'
        verbose_name_plural = 'Modelli stampa pass'
    def __str__(self) -> str:
        return self.nome_template
    
# rappresenta i metadati associati al modello Pass es. Nome Cognome oppure targa o Foto identificativa    
class MetadatoModelloBadge(models.Model):
    PVC_GENERICO='GENERICO'
    PVC_COMUNE='COMUNE'
    PVC_PARTICOLARE='PARTICOLARE'
    TIPI_PVC = [
        (PVC_GENERICO,'Generico'),
        (PVC_COMUNE,'Personale comune (art. 6)'),
        (PVC_PARTICOLARE,'Personale particolare (art. 9)'),]
    PVC_SENSIBILI=[PVC_COMUNE,PVC_PARTICOLARE]
    TP_STRING='STRING'
    TP_TEXT='TEXT'
    TP_DATE='DATE'
    TP_FILE='FILE'
    TP_IMAGE='IMAGE'
    TP_HTML='HTML'
    TIPI_METADATO = [
        (TP_STRING, 'Stringa'),
        (TP_TEXT, 'Testo'),
        (TP_DATE, 'Data'),
        (TP_FILE, 'File'),
        (TP_IMAGE, 'Image'),
        (TP_HTML, 'Testo HTML'),]
    modello_stampa_badge = models.ForeignKey(ModelloStampaBadge, on_delete=models.CASCADE,null=False)   
    nome = models.CharField(max_length=100,null=False,help_text="nome metadato univoco")
    tipo_metadato = models.CharField(
        max_length=6,
        choices=TIPI_METADATO,
        default='STRING',
        null=False
    )
    x_print=models.DecimalField(null=True,blank=True,help_text="coordinata bottom left origin in mm dove stampare il campo",max_digits=5,decimal_places=2)
    y_print=models.DecimalField(null=True,blank=True,help_text="coordinata bottom left origin in mm dove stampare il campo",max_digits=5,decimal_places=2)
    font_size=models.IntegerField(null=True,blank=True,help_text="dimensione del font, se vuoto verrà utilizzato 14")
    font_type=models.CharField(null=True,blank=True,max_length=100,help_text="Font type, se vuoto verrà utilizzato il font default Courier, testati Times-Roman e Helvetica")
    stampabile=models.BooleanField(default=False)
    privato=models.BooleanField(default=False)
    obbligatorio=models.BooleanField(default=False)
    width=models.DecimalField(null=True,blank=True,help_text="larghezza metadato immagine in mm, se null verrà presa la larghezza dell'immagine",default=15,max_digits=5,decimal_places=2)
    height=models.DecimalField(null=True,blank=True,help_text="altezza metadato immagine in mm, se null verrà presa la larghezza dell'immagine",default=15,max_digits=5,decimal_places=2)
    tipo_pvc = models.CharField(
        max_length=12,
        choices=TIPI_PVC,
        default='GENERICO',
        null=False,
        verbose_name="Tipologia dato privacy"
    )
    #creazione dell'indice univoco tra Pass e metadato
    class Meta:
        unique_together = ('modello_stampa_badge', 'nome')
    def __str__(self) -> str:
        return str(self.modello_stampa_badge) + ' - ' +self.nome
    class Meta:
        verbose_name = 'modello metadato'
        verbose_name_plural = 'modelli metadato'
    
class Serie(models.Model):
    nome = models.CharField(unique=True,max_length=100,null=False,help_text="nome univoco della serie Pass(è legata normalmente ad un evento)")
    descrizione = models.TextField(max_length=400,help_text="descrizione della serie")
    data_inizio_validita = models.DateField(null=False, help_text="data inizio validità")
    data_fine_validita = models.DateField(null=True,blank=True, help_text="data fine validità")
    sigla = models.CharField(unique=True,blank=False,max_length=5,null=False,help_text="sigla univoca per la serie")
    progr_emissione = models.IntegerField(null=False,default=0, help_text="progressivo univoco di emissione dei ticket")
    def __str__(self) -> str:
        return self.nome

class SottoSerie(models.Model):
    nome = models.CharField(max_length=100,null=False,help_text="nome univoco della sotto serie Pass")
    descrizione = models.TextField(max_length=400,help_text="descrizione della sotto serie")
    data_inizio_validita = models.DateField(null=False, help_text="data inizio validità")
    data_fine_validita = models.DateField(null=True,blank=True,help_text="data fine validità") 
    serie = models.ForeignKey(Serie, on_delete=models.CASCADE,null=False)   
    modello_stampa_badge = models.ForeignKey(ModelloStampaBadge, on_delete=models.CASCADE,null=False)   
    #creazione dell'indice univoco tra serie e nome
    class Meta:
        unique_together = ('serie', 'nome')
    def __str__(self) -> str:
        return self.nome
    
class Badge(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descrizione = models.CharField(max_length=80,null=False,
                                   help_text="descrizione del Pass, normalmente nome e cognome intestatario oppure contiene l'identificativo univoco dell'entità a cui è associato"
                                   ,default='descrizione Pass')
    sotto_serie = models.ForeignKey(SottoSerie, on_delete=models.CASCADE,null=False,verbose_name='Tipo Pass') 
    codice = models.CharField(max_length=10,null=False,unique=True,
                                   help_text="codice autogenerato fatto da sigla_serie-numero")
    data_inizio_validita = models.DateField(null=False, help_text="data inizio validità")
    data_fine_validita = models.DateField(null=True,blank=True,help_text="data fine validità") 
    @property
    def is_valido(self):
        return date.today() >= self.data_inizio_validita and \
            ( not(self.data_fine_validita) or self.data_fine_validita>=date.today())
    
    def __str__(self) -> str:
        return self.descrizione
    class Meta:
        verbose_name = 'pass'
        verbose_name_plural = 'pass'
    
class MetadatoBadge(RenameFilesModel):
    RENAME_FILES = {
        'valore_image': {'dest': get_file_entity_path}
        ,'valore_file': {'dest': get_file_entity_path}
        }
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE,null=False)   
    metadato = models.ForeignKey(MetadatoModelloBadge, on_delete=models.CASCADE,null=False)
    valore_testo = models.TextField(null=True,blank=True,max_length=1096)
    valore_image = models.ImageField(null=True,blank=True,max_length=255,upload_to="uploads/temp",verbose_name='immagine')   
    valore_file = models.FileField(null=True,blank=True,max_length=255,upload_to="uploads/temp")   
    valore_data = models.DateField(null=True,blank=True)
    #creazione dell'indice univoco tra Pass e metadato
    class Meta:
        unique_together = ('badge', 'metadato')
    def __str__(self) -> str:
        return self.badge.descrizione + ' - ' + self.metadato.nome
    class Meta:
        verbose_name = 'metadato pass'
        verbose_name_plural = 'metadati pass'

    
@receiver(pre_save, sender=Badge)
def hook_save_badge(sender, **kwargs):
    instance:Badge=kwargs['instance']
    if Badge.objects.filter(pk=instance.pk).count()==0:
        genera_codice(instance=instance)
        #preinserisci_metadati(instance)

# generazione del codice univoco del badge da sigla e progressivo
def genera_codice(instance:Badge):
    logger.info("generazione codice Pass "+instance.descrizione+" uuid: "+str(instance.id))
    # caso inserimento
    serie=Serie.objects.get(pk=instance.sotto_serie.serie.pk)
    prog_emissione=serie.progr_emissione+1
    serie.progr_emissione=prog_emissione
    codice=serie.sigla+'-'+str(prog_emissione).zfill(3)
    instance.codice=codice
    serie.save()

#generazione dei metadati alla creazione del pass
def preinserisci_metadati(instance:Badge):    
    sotto_serie_obj=SottoSerie.objects.get(pk=instance.sotto_serie.id)
    fkey_metadati=sotto_serie_obj.modello_stampa_badge.pk
    modelloMetadati=MetadatoModelloBadge.objects.filter(modello_stampa_badge_id=fkey_metadati)
    for modelloMetadato in modelloMetadati:
        MetadatoBadge.objects.create(badge_id=instance.pk,metadato_id=modelloMetadato.pk)

#
def crea_metadati(instance:MetadatoModelloBadge):    
    sotto_series=SottoSerie.objects.filter(modello_stampa_badge__pk=instance.modello_stampa_badge.id)
    for sotto_serie in sotto_series:
        badgeSet=Badge.objects.filter(sotto_serie__id=sotto_serie.id)
        for badge in badgeSet:
            MetadatoBadge.objects.create(badge_id=badge.id,metadato_id=instance.pk)

@receiver(post_save, sender=Badge)
def hook_post_save_badge(sender, **kwargs):
    instance:Badge=kwargs['instance']
    created:Badge=kwargs['created']
    if created:
        preinserisci_metadati(instance)
        
@receiver(post_save, sender=MetadatoModelloBadge)
def hook_post_save_metadato_modello(sender, **kwargs):
    instance:MetadatoModelloBadge=kwargs['instance']
    created:MetadatoModelloBadge=kwargs['created']
    if created:
        crea_metadati(instance)        

# relazione tra utente e Serie e relativo ruolo (gestore o checker)
class UserSeries(models.Model):
    TP_CHECKER='CHECKER'
    TP_GESTORE='GESTORE'
    TIPI_RUOLI = [
        (TP_CHECKER, 'Verificatore'),
        (TP_GESTORE, 'Gestore'),]
    ruolo = models.CharField(
        max_length=20,
        choices=TIPI_RUOLI,
        default=TP_CHECKER,
        null=False
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    serie = models.ForeignKey(Serie, on_delete=models.CASCADE,null=False,related_name="user_series")   
    data_inizio_validita = models.DateField(null=False, help_text="data inizio validità")
    data_fine_validita = models.DateField(null=True,blank=True,help_text="data fine validità") 
    #creazione dell'indice univoco tra utente e serie
    class Meta:
        unique_together = ('user', 'serie',)
        verbose_name = 'ruolo su serie per utente'
        verbose_name_plural = 'ruoli su serie per utente'
    def __str__(self) -> str:
        return self.user.username + ' - ' + self.serie.nome
    
def offusca_dati_personali(pass_obj:Badge):
    """elimina i file per i metadati di tipo TP_IMAGE e TP_FILE e per gli altri tipi offusca con ***

    Args:
        pass_obj (Badge): pass sul quale offuscare i dati personali
    """
    metadati = MetadatoBadge.objects.filter(badge__id=pass_obj.id)
    for metadato in metadati:
        #prelevo il relativo modello di metadato
        modelloMetadato=MetadatoModelloBadge.objects.get(pk=metadato.metadato.id)
        if modelloMetadato and modelloMetadato.tipo_pvc in MetadatoModelloBadge.PVC_SENSIBILI:
            if modelloMetadato.tipo_metadato in [MetadatoModelloBadge.TP_DATE]:
                metadato.valore_data=None
            elif modelloMetadato.tipo_metadato in [MetadatoModelloBadge.TP_HTML,MetadatoModelloBadge.TP_STRING,MetadatoModelloBadge.TP_TEXT]:
                new_val=""
                for char_item in metadato.valore_testo:
                    if not char_item==' ':
                        new_val+='*'
                    else:
                        new_val+=char_item
                metadato.valore_testo=new_val
            elif metadato.valore_image and modelloMetadato.tipo_metadato in [MetadatoModelloBadge.TP_IMAGE]:
                if metadato.valore_image.path:
                    os.remove(metadato.valore_image.path)
                    metadato.valore_image=None
            elif metadato.valore_file and modelloMetadato.tipo_metadato in [MetadatoModelloBadge.TP_FILE]:
                if metadato.valore_file.path:
                    os.remove(metadato.valore_file.path)
                    metadato.valore_file=None
            metadato.save()


def offusca_dati_personali_serie(serie_obj:Serie):
    """offuscamento dati personali per tutti i pass della serie

    Args:
        pass_obj (Badge): pass sul quale offuscare i dati personali
    """
    pass_list=Badge.objects.filter(sotto_serie__serie__id=serie_obj.id)
    for passObj in pass_list:
        offusca_dati_personali(passObj)

def offusca_dati_personali_sottoserie(sottoserie_obj:SottoSerie):
    """offuscamento dati personali per tutti i pass della serie

    Args:
        pass_obj (Badge): pass sul quale offuscare i dati personali
    """
    pass_list=Badge.objects.filter(sotto_serie__id=sottoserie_obj.id)
    for passObj in pass_list:
        offusca_dati_personali(passObj)        
        
class ApiKey(models.Model):
    sotto_serie = models.ForeignKey(SottoSerie, on_delete=models.CASCADE,null=False)   
    key = models.CharField(max_length=255,help_text="key")
    data_inizio_validita = models.DateField(null=False, help_text="data inizio validità")
    data_fine_validita = models.DateField(null=True,blank=True,help_text="data fine validità") 
    #creazione dell'indice univoco tra serie e key
    class Meta:
        unique_together = ('sotto_serie', 'key')
    def __str__(self) -> str:
        return self.sotto_serie.nome
        