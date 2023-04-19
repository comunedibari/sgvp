import django_filters

from .permission import user_sotto_series_from_username
from .models import Badge, MetadatoModelloBadge, ModelloStampaBadge, Serie, SottoSerie, UserSeries

class BadgeFilter(django_filters.FilterSet):
    descrizione = django_filters.CharFilter(lookup_expr='icontains')
    sotto_serie = django_filters.ModelChoiceFilter(queryset=SottoSerie.objects.all())
    
    # effettuo override del campo sotto_serie filtrando alle sole sottoserie ammesse all'utente
    def __init__(self, *args, **kwargs):
        username=None
        if 'username' in kwargs:
            username=kwargs.pop('username')
        super().__init__(*args, **kwargs)
        if username:
            self.filters['sotto_serie'] = django_filters.ModelChoiceFilter(
                queryset=user_sotto_series_from_username(username=username,roles=[UserSeries.TP_GESTORE],valid_now=False),
                #queryset=SottoSerie.objects.filter(serie__user_series__user__username=username,serie__user_series__ruolo=UserSeries.TP_GESTORE))
            )
    
    class Meta:
        model = Badge
        fields = ['sotto_serie', 'codice', 'descrizione']


class ModelloStampaBadgeFilter(django_filters.FilterSet):
    nome_template = django_filters.CharFilter(lookup_expr='icontains',label="Nome modello contiene")
    
    class Meta:
        model = ModelloStampaBadge
        fields = ['nome_template']


class MetadatoModelloBadgeFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(lookup_expr='icontains',label="Nome metadato contiene")
    
    class Meta:
        model = MetadatoModelloBadge
        fields = ['nome','tipo_metadato']


class SerieFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(lookup_expr='icontains',label="Nome contiene")
    
    class Meta:
        model = Serie
        fields = ['nome']


class SottoSerieFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(lookup_expr='icontains',label="Nome contiene")
    
    class Meta:
        model = SottoSerie
        fields = ['nome']
