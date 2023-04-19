
from django.utils import timezone
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from badge.models import ModelloStampaBadge
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from badge.filter import ModelloStampaBadgeFilter
from badge.permission import BaseStaffOrSuperuserView
from badge.views.utils import add_deleted_objects, add_role
from django.contrib.messages.views import SuccessMessageMixin
    
class ModelloStampaBadgeCreateView(SuccessMessageMixin,BaseStaffOrSuperuserView,CreateView):
    model = ModelloStampaBadge
    fields = ['nome_template','file_sfondo','x_px_qr','y_px_qr','version','box_size','border','width','height','x_print_codice','y_print_codice','font_size_codice']
    template_name = "badge/modello/modello_edit.html"
    success_url = reverse_lazy('modellostampa-list')
    success_message = "Modello <b>%(nome_template)s</b> creato con successo !!!"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        add_role(self.request,context)
        context['is_create'] = True
        return context
    
class ModelloStampaBadgeUpdateView(SuccessMessageMixin,BaseStaffOrSuperuserView,UpdateView):
    model = ModelloStampaBadge
    fields = ['nome_template','file_sfondo','x_px_qr','y_px_qr','version','box_size','border','width','height','x_print_codice','y_print_codice','font_size_codice']
    template_name = "badge/modello/modello_edit.html"
    success_message = "Modello <b>%(nome_template)s</b> salvato con successo !!!"
    
    def get_success_url(self):
          pk=self.kwargs['pk']
          return reverse_lazy('modellostampa-update', kwargs={'pk': pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = False
        add_role(self.request,context)
        return context
     

class ModelloStampaBadgeDeleteView(SuccessMessageMixin,BaseStaffOrSuperuserView,DeleteView):
    model = ModelloStampaBadge
    success_url = reverse_lazy('modellostampa-list')
    template_name = "badge/modello/modello_delete.html"
    
    def get_success_message(self,cleaned_data):
        return f"Modello <b>%s</b>eliminato con successo !!!" % self.object.nome_template
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = False
        context['url_successo'] = reverse_lazy('modellostampa-list')
        add_role(self.request,context)
        add_deleted_objects(self.request,context,self.object)
        return context
    
class ModelloStampaBadgeListView(BaseStaffOrSuperuserView, ListView):
    """generic class based view con accesso limitato ai soli utenti autenticati e con is_staff_or_superuser
    @see https://cpadiernos.github.io/function-based-views-and-their-class-based-view-equivalents-in-django-part-one.html

    Args:
        LoginRequiredMixin (_type_): _description_
        UserPassesTestMixin (_type_): _description_
        ListView (_type_): _description_

    Returns:
        _type_: _description_
    """
    ordering = ['-id']
    model = ModelloStampaBadge
    paginate_by = 5  # if pagination is desired
    template_name = "badge/modello/modello_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        add_role(self.request,context)
        context['now'] = timezone.now()
        context['filter'] = ModelloStampaBadgeFilter(self.request.GET, queryset = self.get_queryset())
        #inserisco nella variabile di contesto parameters la attuale query string al netto della page in
        #modo da non perdere i filtri impostati quando uso la pagina
        get_copy = self.request.GET.copy()
        parameters = get_copy.pop('page', True) and get_copy.urlencode()
        context['parameters'] = parameters
        return context
        
    def get_queryset(self):
        queryset = super().get_queryset()
        qsDef=ModelloStampaBadgeFilter(self.request.GET, queryset=queryset).qs
        return qsDef



