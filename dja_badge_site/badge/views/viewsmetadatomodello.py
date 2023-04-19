
from django import forms
from django.http import HttpResponse
from django.utils import timezone
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from badge.models import MetadatoModelloBadge, ModelloStampaBadge
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from badge.filter import MetadatoModelloBadgeFilter
from badge.permission import BaseStaffOrSuperuserView
from badge.views.utils import add_deleted_objects, add_role
from django.contrib.messages.views import SuccessMessageMixin

class MetadatoModelloBadgeCreateView(SuccessMessageMixin,BaseStaffOrSuperuserView,CreateView):
    model = MetadatoModelloBadge
    fields = ['nome','tipo_metadato','x_print','y_print','font_size','font_type','stampabile','privato','obbligatorio','width','height','tipo_pvc']
    template_name = "badge/modello/metadato/metadatomodello_edit.html"
    success_message = "Metadato <b>%(nome)s</b> creato con successo !!!"
    
    def form_valid(self, form: forms.BaseModelForm) -> HttpResponse:
        pk_modello=self.kwargs['pk_modello']
        modello_stampa=ModelloStampaBadge.objects.get(pk=pk_modello)
        form.instance.modello_stampa_badge=modello_stampa
        return super().form_valid(form)
    
    def get_success_url(self):
          pk_modello=self.kwargs['pk_modello']
          return reverse_lazy('metadatomodello-list', kwargs={'pk': pk_modello})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        add_role(self.request,context)
        context['is_create'] = True
        pk_modello=self.kwargs['pk_modello']
        context['pk_modello'] = pk_modello
        modello_stampa=ModelloStampaBadge.objects.get(pk=pk_modello)
        context['modello_stampa']=modello_stampa
        return context

class MetadatoModelloBadgeUpdateView(SuccessMessageMixin,BaseStaffOrSuperuserView,UpdateView):
    model = MetadatoModelloBadge
    fields = ['nome','tipo_metadato','x_print','y_print','font_size','font_type','stampabile','privato','obbligatorio','width','height','tipo_pvc']
    template_name = "badge/modello/metadato/metadatomodello_edit.html"
    success_message = "Metadato <b>%(nome)s</b> salvato con successo !!!"
    
    def get_success_url(self):
        pk_modello=self.kwargs['pk_modello']
        pk=self.kwargs['pk']
        if self.request.POST['submit']=='salva_e_torna':
            return reverse_lazy('metadatomodello-list', kwargs={'pk': pk_modello})    
        else:
            return reverse_lazy('metadatomodello-update', kwargs={'pk_modello': pk_modello,'pk':pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        add_role(self.request,context)
        context['is_create'] = False
        pk_modello=self.kwargs['pk_modello']
        context['pk_modello'] = pk_modello
        modello_stampa=ModelloStampaBadge.objects.get(pk=pk_modello)
        context['modello_stampa']=modello_stampa
        return context

class MetadatoModelloBadgeDeleteView(SuccessMessageMixin,BaseStaffOrSuperuserView,DeleteView):
    model = MetadatoModelloBadge
    template_name = "badge/modello/metadato/metadatomodello_delete.html"
    
    def get_success_message(self,cleaned_data):
        return f"Metadato <b>%s</b>eliminato con successo !!!" % self.object.nome
    
    def get_success_url(self):
        pk_modello=self.kwargs['pk_modello']
        return reverse_lazy('metadatomodello-list', kwargs={'pk': pk_modello})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        add_role(self.request,context)
        add_deleted_objects(self.request,context,self.object)
        context['is_create'] = False
        pk_modello=self.kwargs['pk_modello']
        context['pk_modello'] = pk_modello
        context['url_successo']=reverse_lazy('metadatomodello-list', kwargs={'pk': pk_modello})
        return context
    
class MetadatoModelloBadgeListView(BaseStaffOrSuperuserView, ListView):
    """generic class based view con accesso limitato ai soli utenti autenticati e con is_staff_or_superuser
    @see https://cpadiernos.github.io/function-based-views-and-their-class-based-view-equivalents-in-django-part-one.html

    Args:
        LoginRequiredMixin (_type_): _description_
        UserPassesTestMixin (_type_): _description_
        ListView (_type_): _description_

    Returns:
        _type_: _description_
    """
    model = MetadatoModelloBadge
    paginate_by = 5  # if pagination is desired
    template_name = "badge/modello/metadato/metadatomodello_list.html"
    ordering = ['-id']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        add_role(self.request,context)
        context['now'] = timezone.now()
        context['filter'] = MetadatoModelloBadgeFilter(self.request.GET, queryset = self.get_queryset())
        context['pk'] =self.kwargs['pk']
        #inserisco nella variabile di contesto parameters la attuale query string al netto della page in
        #modo da non perdere i filtri impostati quando uso la pagina
        get_copy = self.request.GET.copy()
        parameters = get_copy.pop('page', True) and get_copy.urlencode()
        context['parameters'] = parameters
        
        pk_modello=self.kwargs['pk']
        context['pk_modello'] = pk_modello
        modello_stampa=ModelloStampaBadge.objects.get(pk=pk_modello)
        context['modello_stampa']=modello_stampa
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()
        qsDef=MetadatoModelloBadgeFilter(self.request.GET, queryset=queryset).qs
        qsDef=qsDef.filter(modello_stampa_badge__id=self.kwargs['pk'])
        return qsDef



