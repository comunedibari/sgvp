import datetime
import io
import os
from django.contrib import messages
import uuid
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.urls import reverse
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import mm
from ..permission import has_role, has_role_on_serie, is_gestore, is_staff_or_superuser, user_in_request,  user_roles, user_sotto_series
from badge.views.utils import add_role
from ..filter import BadgeFilter
from ..utils import build_image_w_text, genera_qrcode
from ..forms import BadgeEditForm, BadgeNewForm,  MetadatoBadgeForm
from ..models import Badge, MetadatoModelloBadge,Serie,SottoSerie,MetadatoBadge,ModelloStampaBadge, UserSeries, offusca_dati_personali
from django.contrib.auth.decorators import user_passes_test
from django.views.generic.list import ListView
from django.utils.text import slugify
from django.contrib.auth.mixins import UserPassesTestMixin,LoginRequiredMixin
from django.core.exceptions import PermissionDenied

# Create your views here.

# restituisce true in caso di superuser o staff o utente che appartiene al gruppo badge_viewer

# dettaglio badge pubblica con filtro su attriibuti privati
def badge_detail_by_id(request,badge_id:uuid):
    is_gestore=has_role(request=request,role=UserSeries.TP_GESTORE)
    is_stf_or_su=is_staff_or_superuser(user_in_request(request=request))
    badgeObj = get_object_or_404(Badge, pk=badge_id)
    sottoSerieObj = SottoSerie.objects.get(pk=badgeObj.sotto_serie.id)
    serieObj = Serie.objects.get(pk=sottoSerieObj.serie.id)
    modelloStampaBadgeObj = ModelloStampaBadge.objects.get(pk=sottoSerieObj.modello_stampa_badge.id)
    #filtro i metadati privati 
    has_bvr=has_role_on_serie(request,serie=badgeObj.sotto_serie.serie,roles=[UserSeries.TP_CHECKER])
    if has_bvr:
        metadati = MetadatoBadge.objects.filter(badge__id=badge_id)
    else:
        metadati = MetadatoBadge.objects.filter(badge__id=badge_id,metadato__privato=False)    
    return render(request, 'badge/detail.html', {'badge': badgeObj,
                                                 'sottoSerie':sottoSerieObj,
                                                 'serie':serieObj,
                                                 'modelloStampaBadge':modelloStampaBadgeObj,
                                                 'metadati':metadati,
                                                 'is_gestore':is_gestore,
                                                 'is_stf_or_su':is_stf_or_su,
                                                 'is_staff_or_superuser':is_staff_or_superuser(user_in_request(request))})
# file PDF badge
@user_passes_test(is_gestore)
def badge_print_by_id(request,badge_id:uuid):
    badgeObj = get_object_or_404(Badge, pk=badge_id)
    sottoSerieObj = SottoSerie.objects.get(pk=badgeObj.sotto_serie.id)
    has_bvr=has_role_on_serie(request,serie=sottoSerieObj.serie,roles=[UserSeries.TP_GESTORE])
    if not has_bvr:
        raise PermissionDenied
    modelloStampaBadgeObj = ModelloStampaBadge.objects.get(pk=sottoSerieObj.modello_stampa_badge.id)
    metadati = MetadatoBadge.objects.filter(badge__id=badge_id)
    urlBadge=request.build_absolute_uri()
    originUrlDetail = os.environ.get('ORIGIN_URL_PASS_DETAIL','')
    if originUrlDetail:
        urlBadge=originUrlDetail.replace('{badge_id}',str(badge_id))
    buffer=genera_pass(modelloStampaBadgeObj,urlBadge,badgeObj.codice,metadati,mockImage=None)
    return FileResponse(buffer, as_attachment=True, filename=str(badge_id)+'.pdf')    

def genera_pass(modelloStampaBadgeObj:ModelloStampaBadge,urlBadge:str,codice_badge:str,metadatiQuerySet,mockImage:ImageReader)->io.BytesIO:
    #generazione pass in pdf 
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()
    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)
    append_pass(modelloStampaBadgeObj,urlBadge,codice_badge,metadatiQuerySet,mockImage,p)
    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

def append_pass(modelloStampaBadgeObj:ModelloStampaBadge,urlBadge:str,codice_badge:str,metadatiQuerySet,mockImage:ImageReader,p:canvas.Canvas):
    # Create the PDF object, using the buffer as its "file."
    # set page in points
    dimensione_pagina_tuple=(float(modelloStampaBadgeObj.width)*mm,float(modelloStampaBadgeObj.height)*mm)
    p.setPageSize(dimensione_pagina_tuple)
    sfondo= ImageReader(modelloStampaBadgeObj.file_sfondo.file)
    p.drawImage(image=sfondo,x=0,y=0,mask='auto',width=float(modelloStampaBadgeObj.width)*mm,height=float(modelloStampaBadgeObj.height)*mm) 
    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    # generazione qrcode
    img_qrcode=genera_qrcode(urlBadge,modelloStampaBadgeObj.box_size,modelloStampaBadgeObj.border,modelloStampaBadgeObj.version,'H')
    p.drawImage(image=ImageReader(img_qrcode),x=float(modelloStampaBadgeObj.x_px_qr)*mm,y=float(modelloStampaBadgeObj.y_px_qr)*mm,mask='auto') 
    #stampa dei metadati
    for metadato in metadatiQuerySet:
        #prelevo il relativo modello di metadato
        modelloMetadato=MetadatoModelloBadge.objects.get(pk=metadato.metadato.id)
        if modelloMetadato and modelloMetadato.stampabile:
            if modelloMetadato.tipo_metadato in (MetadatoModelloBadge.TP_STRING,MetadatoModelloBadge.TP_TEXT,MetadatoModelloBadge.TP_DATE,MetadatoModelloBadge.TP_HTML):
                font_size=14
                font_type='Courier'
                if modelloMetadato.font_type:
                    font_type=modelloMetadato.font_type
                if modelloMetadato.font_size:
                    font_size=modelloMetadato.font_size
                p.setFont(font_type,font_size)
                testo=metadato.valore_testo
                if modelloMetadato.tipo_metadato == MetadatoModelloBadge.TP_DATE:
                    testo=metadato.valore_data
                elif modelloMetadato.tipo_metadato == MetadatoModelloBadge.TP_STRING:
                    testo=metadato.valore_testo    
                if testo:    
                    p.drawString(float(modelloMetadato.x_print)*mm, float(modelloMetadato.y_print)*mm, testo)        
            elif modelloMetadato.tipo_metadato in (MetadatoModelloBadge.TP_IMAGE) and (metadato.valore_image or mockImage):
                if not mockImage:
                    ir=ImageReader(metadato.valore_image.file)
                else:
                    ir=mockImage
                if modelloMetadato.width>0 and modelloMetadato.height>0:
                    p.drawImage(image=ir,x=float(modelloMetadato.x_print)*mm,y=float(modelloMetadato.y_print)*mm,width=float(modelloMetadato.width)*mm,height=float(modelloMetadato.height)*mm,mask='auto') 
                else:
                    p.drawImage(image=ir,x=float(modelloMetadato.x_print)*mm,y=float(modelloMetadato.y_print)*mm,mask='auto') 
    # stampa del codice             
    if modelloStampaBadgeObj.x_print_codice and modelloStampaBadgeObj.y_print_codice:
        font_size_codice=14
        if modelloStampaBadgeObj.font_size_codice:
            font_size_codice=modelloStampaBadgeObj.font_size_codice
        p.setFont("Courier",font_size_codice)
        p.drawString(float(modelloStampaBadgeObj.x_print_codice)*mm, float(modelloStampaBadgeObj.y_print_codice)*mm, codice_badge)                    

    
def homepage(request):
    is_gestore=has_role(request=request,role=UserSeries.TP_GESTORE)
    is_stf_or_su=is_staff_or_superuser(user_in_request(request=request))
    mySottoserie=user_roles(username=user_in_request(request).username,roles=[UserSeries.TP_GESTORE,UserSeries.TP_CHECKER])
    return render(request, 'badge/home.html',
                  {
                      'is_gestore':is_gestore,
                      'is_stf_or_su':is_stf_or_su,
                      'mySottoserie':mySottoserie
                   })

# pagina nuovo badge
@user_passes_test(is_gestore)
def new_badge(request):
    is_gestore=has_role(request=request,role=UserSeries.TP_GESTORE)
    is_stf_or_su=is_staff_or_superuser(user_in_request(request=request))
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = BadgeNewForm(request.POST)
        if form.is_valid():
            raw_data=form.cleaned_data
            sotto_serie=SottoSerie.objects.get(pk=raw_data['sotto_serie'].id)
            has_bvr=has_role_on_serie(request,serie=sotto_serie.serie,roles=[UserSeries.TP_GESTORE])
            if not has_bvr:
                raise PermissionDenied
            new_badge=Badge.objects.create(sotto_serie_id=int(raw_data['sotto_serie'].id),
                                 descrizione=raw_data['descrizione'],
                                data_inizio_validita=raw_data['data_inizio_validita']
                                ,data_fine_validita=raw_data['data_fine_validita'])
            # check whether it's valid:
            messages.success(request, "Pass creato con successo !!!")
            return redirect('badge_edit', badge_id=new_badge.id)
    # if a GET (or any other method) we'll create a blank form
    else:
        form = BadgeNewForm(user=request.user)
    return render(request, 'badge/pass/badge_create.html', {
        'form': form,
        'is_gestore':is_gestore,
        'is_stf_or_su':is_stf_or_su
        })


# pagina di edit badge 
@user_passes_test(is_gestore)
def badge_edit(request,badge_id:uuid):
    badgeObj = get_object_or_404(Badge, pk=badge_id)
    is_gestore=has_role(request=request,role=UserSeries.TP_GESTORE)
    is_stf_or_su=is_staff_or_superuser(user_in_request(request=request))
    has_bvr=has_role_on_serie(request,serie=badgeObj.sotto_serie.serie,roles=[UserSeries.TP_GESTORE])
    if not has_bvr:
        raise PermissionDenied
    url_download_badge=reverse('badge_print_by_id',kwargs={'badge_id':badgeObj.pk})
    metadati = MetadatoBadge.objects.filter(badge_id=badgeObj.id)
    model_metadati_notext = MetadatoBadge.objects.filter(badge_id=badgeObj.id,metadato__tipo_metadato__in=[MetadatoModelloBadge.TP_FILE,MetadatoModelloBadge.TP_IMAGE])
    metadati_notext=[]
    for mnotext in model_metadati_notext:
        url=None
        file_name=None    
        if mnotext.metadato.tipo_metadato==MetadatoModelloBadge.TP_IMAGE:
            valore=mnotext.valore_image
        elif mnotext.metadato.tipo_metadato==MetadatoModelloBadge.TP_FILE:    
            valore=mnotext.valore_file
        if valore.name:    
            url=valore.url
            file_name=valore.name    
        metadatoObj={'id':mnotext.pk,
                     'nome':mnotext.metadato.nome,
                     'url':url,
                     'file_name':file_name,
                     'tipo_metadato':mnotext.metadato.tipo_metadato,
                     'is_gestore':is_gestore,
                     'is_stf_or_su':is_stf_or_su,
                     'url_edit':reverse('badge_edit_metadato',kwargs={'id':mnotext.pk})
                     }
        metadati_notext.append(metadatoObj)
    ##mi genero la lista dei metadati di tipo file e immagine e li renderizzo con url o link to edit
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = BadgeEditForm(request.POST,request.FILES,badgeObj=badgeObj)
        if form.is_valid():
            raw_data=form.cleaned_data
            badgeObj.descrizione=raw_data['descrizione']
            badgeObj.data_inizio_validita=raw_data['data_inizio_validita']
            badgeObj.data_fine_validita=raw_data['data_fine_validita']
            badgeObj.save()
            #salvataggio dei metadati
            for key in raw_data:
                if key.startswith('metadato_') and not key.endswith('clear'):
                    metadato_id=key[9:]
                    metadato=MetadatoBadge.objects.get(pk=metadato_id)
                    if metadato.metadato.tipo_metadato==MetadatoModelloBadge.TP_TEXT \
                        or metadato.metadato.tipo_metadato==MetadatoModelloBadge.TP_STRING \
                        or metadato.metadato.tipo_metadato==MetadatoModelloBadge.TP_HTML:
                        metadato.valore_testo=raw_data[key]
                        metadato.save()
                    elif metadato.metadato.tipo_metadato==MetadatoModelloBadge.TP_DATE:
                        metadato.valore_data=raw_data[key]
                        metadato.save()    
            messages.success(request,"Salvataggio effettuato con successo")                       
            if request.POST['submit']=="salva_e_torna":
                return redirect('lista_badge')
            else:    
                return render(request, 'badge/pass/badge_edit.html', 
                            {'form': form,
                            'badge':badgeObj,
                            'url_download_badge':url_download_badge,
                            'metadati_notext':metadati_notext,
                            'is_gestore':is_gestore,
                            'is_stf_or_su':is_stf_or_su,
                            })        
        else:
            messages.warning(request,"Controllare i campi errati!")
            return render(request, 'badge/pass/badge_edit.html', 
                          {'form': form,
                           'badge':badgeObj,
                           'url_download_badge':url_download_badge,
                           'metadati_notext':metadati_notext,
                           'is_gestore':is_gestore,
                           'is_stf_or_su':is_stf_or_su
                           })        
    # if a GET (or any other method) we'll create a blank form
    else:
        formData={
            'data_inizio_validita':badgeObj.data_inizio_validita
            ,'data_fine_validita':badgeObj.data_fine_validita
            ,'descrizione':badgeObj.descrizione
            }
        for metadato in metadati:
            if metadato.metadato.tipo_metadato==MetadatoModelloBadge.TP_DATE:
                formData.update([('metadato_'+str(metadato.id),metadato.valore_data)])
            elif metadato.metadato.tipo_metadato==MetadatoModelloBadge.TP_TEXT \
                    or metadato.metadato.tipo_metadato==MetadatoModelloBadge.TP_STRING \
                    or metadato.metadato.tipo_metadato==MetadatoModelloBadge.TP_HTML:
                formData.update([('metadato_'+str(metadato.id),metadato.valore_testo)])    
        form = BadgeEditForm(initial=formData,badgeObj=badgeObj)
    return render(request, 'badge/pass/badge_edit.html', 
                  {'form': form,
                   'badge':badgeObj,
                   'is_gestore':is_gestore,
                   'is_stf_or_su':is_stf_or_su,
                   'url_download_badge':url_download_badge,
                   'metadati_notext':metadati_notext})        


# pagina di edit metadato badge 
@user_passes_test(is_gestore)
def badge_edit_metadato(request,id:int):
    
    def elimina_field(form:MetadatoBadgeForm,metadato:MetadatoBadge):
        if metadato.metadato.tipo_metadato==MetadatoModelloBadge.TP_FILE:
            form.fields.pop('valore_image')
        elif metadato.metadato.tipo_metadato==MetadatoModelloBadge.TP_IMAGE:    
            form.fields.pop('valore_file')
            
    template='badge/metadato/metadato.html'
    metadato=get_object_or_404(MetadatoBadge, pk=id)
    has_bvr=has_role_on_serie(request,serie=metadato.badge.sotto_serie.serie,roles=[UserSeries.TP_GESTORE])
    is_gestore=has_role(request=request,role=UserSeries.TP_GESTORE)
    is_stf_or_su=is_staff_or_superuser(user_in_request(request=request))
    if not has_bvr:
        raise PermissionDenied
    url_edit_badge=reverse('badge_edit',kwargs={'badge_id':metadato.badge.pk})
    metadatoObj={
        'nome':metadato.metadato.nome,
        'nome_badge':metadato.badge.descrizione,
        'codice_badge':metadato.badge.codice,
    }
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = MetadatoBadgeForm(request.POST,request.FILES,instance=metadato)
        if form.is_valid():
            form.save()
            form = MetadatoBadgeForm(instance=metadato)    
            messages.success(request,"Metadato salvato con successo!")
            elimina_field(form=form,metadato=metadato)    
            return redirect('badge_edit', badge_id=metadato.badge.id)
        else:
            messages.warning(request,"Controllare i campi errati!")
            return render(request, template, {'form': form,
                                              'url_edit_badge':url_edit_badge,
                                              'metadatoObj':metadatoObj,
                                              'is_gestore':is_gestore,
                                              'is_stf_or_su':is_stf_or_su,
                                              })        
    else:
        form = MetadatoBadgeForm(instance=metadato)
        elimina_field(form=form,metadato=metadato)    
    return render(request, template, {'form': form,
                                      'url_edit_badge':url_edit_badge,
                                      'metadatoObj':metadatoObj,
                                      'is_gestore':is_gestore,
                                      'is_stf_or_su':is_stf_or_su})        


#preview del badge con codice e QR
@user_passes_test(is_staff_or_superuser)
def badge_preview(request,modello_id):
    """vista per generare la preview del badge a partire dal ModelloStampaBadge

    Args:
        request (_type_): _description_
        modello_id (_type_): _description_

    Returns:
        _type_: HttpResponse
    """
    modelloStampaBadgeObj = get_object_or_404(ModelloStampaBadge, pk=modello_id)
    ####
    mock_uuid="61e1ac1f-1c0c-471f-a172-e4b1283fc40e"
    urlBadge=reverse('badge_detail_by_id',kwargs={'badge_id':mock_uuid})
    originUrlDetail = os.environ.get('ORIGIN_URL_PASS_DETAIL','')
    if originUrlDetail:
        urlBadge=originUrlDetail.replace('{badge_id}',mock_uuid)
    metadati_modello=MetadatoModelloBadge.objects.filter(modello_stampa_badge__id=modelloStampaBadgeObj.pk)
    metadati_mocked=[]
    for metadato_modello in metadati_modello:
        metadato=MetadatoBadge()
        metadato.metadato=metadato_modello
        if metadato_modello.stampabile:
            if metadato_modello.tipo_metadato==MetadatoModelloBadge.TP_TEXT \
                or metadato_modello.tipo_metadato==MetadatoModelloBadge.TP_STRING:
                metadato.valore_testo="VALORE " + metadato_modello.nome
            elif metadato_modello.tipo_metadato==MetadatoModelloBadge.TP_DATE:    
                metadato.valore_data = datetime.now()
            metadati_mocked.append(metadato)
    buffer=genera_pass(modelloStampaBadgeObj,urlBadge,"XXXXX-YYY",metadati_mocked,ImageReader(build_image_w_text("Immagine test")))
    return FileResponse(buffer, as_attachment=True, filename='preview_'+ slugify(modelloStampaBadgeObj.nome_template)+'.pdf')    
    
        
class BadgeListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """generic class based view con accesso limitato ai soli utenti autenticati e con is_gestore
    @see https://cpadiernos.github.io/function-based-views-and-their-class-based-view-equivalents-in-django-part-one.html

    Args:
        LoginRequiredMixin (_type_): _description_
        UserPassesTestMixin (_type_): _description_
        ListView (_type_): _description_

    Returns:
        _type_: _description_
    """
    model = Badge
    paginate_by = 5  # if pagination is desired
    template_name="badge/pass/badge_list.html"
    ordering_key = "o"
    
    def get_ordering(self) -> tuple:
        lista_ordinamento=self.request.GET.getlist(
            self.ordering_key, '-id')
        return lista_ordinamento

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['filter'] = BadgeFilter(self.request.GET, queryset = self.get_queryset(),username=user_in_request(self.request).username)
        #inserisco nella variabile di contesto parameters la attuale query string al netto della page in
        #modo da non perdere i filtri impostati quando uso la pagina
        get_copy = self.request.GET.copy()
        parameters = get_copy.pop('page', True) and get_copy.urlencode()
        context['parameters'] = parameters
        add_role(self.request,context)
        #context["table"] = TableSort(
        #    self.request,
        #    self.object_list,
        #    sort_key_name=self.ordering_key,
        #    table_css_classes="table ",
        #    fields=['sotto_serie__nome','codice','descrizione','is_valido']
        #)
        return context
    
    def test_func(self):
        # test di accesso
        if is_gestore(user_in_request(self.request)):
            return True
        else:
            return False
        
    def get_queryset(self):
        queryset = super().get_queryset()
        qsDef=BadgeFilter(self.request.GET, queryset=queryset).qs
        qsDef=qsDef.filter(sotto_serie__in=user_sotto_series(user=self.request.user,roles=[UserSeries.TP_GESTORE],valid_now=False))
        return qsDef


@user_passes_test(is_gestore)
def print_selected(request):
    qs=Badge.objects \
    .filter(sotto_serie__in=user_sotto_series(user=request.user,roles=[UserSeries.TP_GESTORE],valid_now=False))
    if request.GET.get('sotto_serie'):       
        qs=qs.filter(sotto_serie__pk=request.GET.get('sotto_serie'))
    if request.GET.get('descrizione'):       
        qs=qs.filter(sotto_serie__descrizione__icontains=request.GET.get('descrizione'))
    if request.GET.get('codice'):       
        qs=qs.filter(codice=request.GET.get('codice'))
    buffer = io.BytesIO()
    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)        
    badges=qs.all()    
    for badge in badges:
        modelloStampaBadgeObj = ModelloStampaBadge.objects.get(pk=badge.sotto_serie.modello_stampa_badge.id)    
        metadati = MetadatoBadge.objects.filter(badge__id=badge.id)
        urlBadge=request.build_absolute_uri()
        originUrlDetail = os.environ.get('ORIGIN_URL_PASS_DETAIL','')
        if originUrlDetail:
            urlBadge=originUrlDetail.replace('{badge_id}',str(badge.id))
        append_pass(modelloStampaBadgeObj,urlBadge,badge.codice,metadati,None,p)
        p.showPage()
       # Close the PDF object cleanly, and we're done.
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='pass_output'+'.pdf')    

# pagina di edit badge 
@user_passes_test(is_gestore)
def badge_offusca(request,badge_id:uuid):
    badgeObj = get_object_or_404(Badge, pk=badge_id)
    is_gestore=has_role(request=request,role=UserSeries.TP_GESTORE)
    is_stf_or_su=is_staff_or_superuser(user_in_request(request=request))
    has_bvr=has_role_on_serie(request,serie=badgeObj.sotto_serie.serie,roles=[UserSeries.TP_GESTORE])
    metadati = MetadatoModelloBadge.objects.filter(modello_stampa_badge__pk=badgeObj.sotto_serie.modello_stampa_badge.id,tipo_pvc__in=MetadatoModelloBadge.PVC_SENSIBILI)
    if not has_bvr:
        raise PermissionDenied
    if request.method == 'POST':
        offusca_dati_personali(badgeObj)
        messages.success(request,"Offuscamento effettuato con successo")
        return redirect('badge_edit', badge_id=badgeObj.id)
    else:
        return render(request, 'badge/pass/badge_offusca.html', 
                  {'badge':badgeObj,
                   'is_gestore':is_gestore,
                   'is_stf_or_su':is_stf_or_su,
                   'url_indietro':reverse('badge_edit',kwargs={'badge_id':badgeObj.id}),
                   'metadati':metadati,
                   })        
