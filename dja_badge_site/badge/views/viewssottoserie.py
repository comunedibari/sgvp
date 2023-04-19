
from django import forms
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from badge.models import MetadatoModelloBadge, Serie, SottoSerie, UserSeries, offusca_dati_personali_sottoserie
from django.urls import reverse, reverse_lazy
from django.views.generic.list import ListView
from badge.filter import SottoSerieFilter
from badge.permission import BaseStaffOrSuperuserView, has_role, has_role_on_serie, is_gestore, is_staff_or_superuser, user_in_request
from bootstrap_italia_template.widgets import BootstrapItaliaDateWidget
from badge.views.utils import add_deleted_objects, add_role
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.contrib import messages


class SottoSerieForm(forms.ModelForm):
    class Meta:
        model = SottoSerie
        fields = ['nome','descrizione','modello_stampa_badge','data_inizio_validita','data_fine_validita']
        widgets = {
            'data_inizio_validita': BootstrapItaliaDateWidget(),
            'data_fine_validita': BootstrapItaliaDateWidget(),
        }

class SottoSerieCreateView(SuccessMessageMixin,BaseStaffOrSuperuserView,CreateView):
    model = SottoSerie
    template_name = "badge/generic/item_edit.html"
    form_class=SottoSerieForm
    success_message = "Sottoserie <b>%(nome)s</b> creata con successo !!!"
    
    def form_valid(self, form: forms.BaseModelForm) -> HttpResponse:
        pk_serie=self.kwargs['pk_serie']
        serie=Serie.objects.get(pk=pk_serie)
        form.instance.serie=serie
        return super().form_valid(form)
    
    def get_success_url(self):
          pk_serie=self.kwargs['pk_serie']
          return reverse_lazy('sottoserie-list', kwargs={'pk': pk_serie})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = True
        add_role(self.request,context)
        pk_serie=self.kwargs['pk_serie']
        context['url_successo']=reverse_lazy('sottoserie-list',kwargs={'pk': pk_serie})
        context['nome_oggetto']='Sottoserie'
        context['titolo_back_button']='Torna alla lista'
        return context

class SottoSerieUpdateView(SuccessMessageMixin,BaseStaffOrSuperuserView,UpdateView):
    model = SottoSerie
    template_name = "badge/generic/item_edit.html"
    form_class=SottoSerieForm
    success_message = "Sottoserie <b>%(nome)s</b> creata con successo !!!"
    
    def get_success_url(self):
          pk_serie=self.kwargs['pk_serie']
          return reverse_lazy('sottoserie-list', kwargs={'pk': pk_serie})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = False
        add_role(self.request,context)
        pk_serie=self.kwargs['pk_serie']
        context['url_successo']=reverse_lazy('sottoserie-list',kwargs={'pk': pk_serie})
        context['nome_oggetto']='Sottoserie'
        context['titolo_back_button']='Torna alla lista'
        return context

class SottoSerieDeleteView(SuccessMessageMixin,BaseStaffOrSuperuserView,DeleteView):
    model = SottoSerie
    template_name = "badge/generic/item_delete.html"
    
    def get_success_message(self,cleaned_data):
        return f"Sottoserie <b>%s</b>eliminata con successo !!!" % self.object.nome
    
    def get_success_url(self):
          pk_serie=self.kwargs['pk_serie']
          return reverse_lazy('sottoserie-list', kwargs={'pk': pk_serie})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = False
        add_role(self.request,context)
        add_deleted_objects(self.request,context,self.object)
        pk_serie=self.kwargs['pk_serie']
        context['url_successo']=reverse_lazy('sottoserie-list',kwargs={'pk': pk_serie})
        context['nome_oggetto']='Sotto serie'
        context['identificatore_oggetto']=self.object.nome
        
        return context
    
class SottoSerieListView(BaseStaffOrSuperuserView, ListView):
    """generic class based view con accesso limitato ai soli utenti autenticati e con is_staff_or_superuser
    @see https://cpadiernos.github.io/function-based-views-and-their-class-based-view-equivalents-in-django-part-one.html

    Args:
        LoginRequiredMixin (_type_): _description_
        UserPassesTestMixin (_type_): _description_
        ListView (_type_): _description_

    Returns:
        _type_: _description_
    """
    model = SottoSerie
    paginate_by = 5  # if pagination is desired
    template_name = "badge/sottoserie/sottoserie_list.html"
    ordering = ['-id']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        add_role(self.request,context)
        context['now'] = timezone.now()
        context['filter'] = SottoSerieFilter(self.request.GET, queryset = self.get_queryset())
        #inserisco nella variabile di contesto parameters la attuale query string al netto della page in
        #modo da non perdere i filtri impostati quando uso la pagina
        get_copy = self.request.GET.copy()
        parameters = get_copy.pop('page', True) and get_copy.urlencode()
        context['parameters'] = parameters
        context['pk_serie'] = self.kwargs['pk']
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()
        qsDef=SottoSerieFilter(self.request.GET, queryset=queryset).qs
        qsDef=qsDef.filter(serie__id=self.kwargs['pk'])
        return qsDef
    
    # pagina di edit badge 
@user_passes_test(is_gestore)
def offusca(request,pk_serie,pk):
    serieObj = get_object_or_404(Serie, pk=pk_serie)
    is_gestore=has_role(request=request,role=UserSeries.TP_GESTORE)
    is_stf_or_su=is_staff_or_superuser(user_in_request(request=request))
    has_bvr=has_role_on_serie(request,serie=serieObj,roles=[UserSeries.TP_GESTORE])
    sottoserieObj=get_object_or_404(SottoSerie, pk=pk)
    sottoseries=SottoSerie.objects.filter(pk=pk)
    modelli_stampa=SottoSerie.objects.filter(pk=pk).values('modello_stampa_badge__id').all()
    metadati = MetadatoModelloBadge.objects.filter(modello_stampa_badge__pk__in=modelli_stampa,tipo_pvc__in=MetadatoModelloBadge.PVC_SENSIBILI)
    if not has_bvr:
        raise PermissionDenied
    if request.method == 'POST':
        offusca_dati_personali_sottoserie(sottoserieObj)
        messages.success(request,"Offuscamento effettuato con successo")
        return redirect('sottoserie-list',pk=pk_serie)
    else:
        return render(request, 'badge/pass/badge_offusca.html', 
                  {'sottoseries':sottoseries,
                   'is_gestore':is_gestore,
                   'url_indietro':reverse('sottoserie-list',kwargs={'pk':pk_serie}),
                   'is_stf_or_su':is_stf_or_su,
                   'metadati':metadati,
                   })        
