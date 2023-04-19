from django.urls import path

from .views import viewspass,viewsmodello,viewsmetadatomodello,viewsserie,viewssottoserie,viewstest

urlpatterns = [
    # pubblica
    # alcuni link vengono oscurati a seconda del ruolo
    path('', viewspass.homepage, name='home'),
    # ruolo staff_or_superuser o gestore su serie
    path('<uuid:badge_id>/print', viewspass.badge_print_by_id, name='badge_print_by_id'),
    # pubblico con restrizioni su attributi privati (accessibili solo a ruoli gestore/checker della serie) 
    # e tasto download solo a staff_or_superuser
    path('<uuid:badge_id>/detail', viewspass.badge_detail_by_id, name='badge_detail_by_id'),
    # ruolo staff_or_superuser o gestore su serie
    path('pass/new', viewspass.new_badge, name='new_badge'),
    # ruolo staff_or_superuser o gestore su serie
    path('pass/<uuid:badge_id>/edit', viewspass.badge_edit, name='badge_edit'),
    # ruolo staff_or_superuser o gestore su serie
    path('pass/metadato/<int:id>', viewspass.badge_edit_metadato, name='badge_edit_metadato'),
    # ruolo staff_or_superuser o gestore su serie
    path('pass', viewspass.BadgeListView.as_view(), name='lista_badge'),
    # ruolo staff_or_superuser o gestore su serie
    path('pass/print_selected', viewspass.print_selected, name='print_selected'),
    # ruolo staff_or_superuser o gestore su serie
    path('pass/<uuid:badge_id>/offusca', viewspass.badge_offusca, name='badge_offusca'),
    # /modello .... gestione del modello e metadati
    path('modello', viewsmodello.ModelloStampaBadgeListView.as_view(), name='modellostampa-list'),
    path('modello/add', viewsmodello.ModelloStampaBadgeCreateView.as_view(), name='modellostampa-add'),
    path('modello/<int:pk>', viewsmodello.ModelloStampaBadgeUpdateView.as_view(), name='modellostampa-update'),
    path('modello/<int:pk>/delete', viewsmodello.ModelloStampaBadgeDeleteView.as_view(), name='modellostampa-delete'),
    path('modello/<int:modello_id>/preview',viewspass.badge_preview, name="badge_preview"),
    # metadati modello
    path('modello/<int:pk>/metadato', viewsmetadatomodello.MetadatoModelloBadgeListView.as_view(), name='metadatomodello-list'),
    path('modello/<int:pk_modello>/metadato/add', viewsmetadatomodello.MetadatoModelloBadgeCreateView.as_view(), name='metadatomodello-add'),
    path('modello/<int:pk_modello>/metadato/<int:pk>', viewsmetadatomodello.MetadatoModelloBadgeUpdateView.as_view(), name='metadatomodello-update'),
    path('modello/<int:pk_modello>/metadato/<int:pk>/delete', viewsmetadatomodello.MetadatoModelloBadgeDeleteView.as_view(), name='metadatomodello-delete'),
    # serie
    path('serie', viewsserie.SerieListView.as_view(), name='serie-list'),
    path('serie/add', viewsserie.SerieCreateView.as_view(), name='serie-add'),
    path('serie/<int:pk>', viewsserie.SerieUpdateView.as_view(), name='serie-update'),
    path('serie/<int:pk>/delete', viewsserie.SerieDeleteView.as_view(), name='serie-delete'),
    path('serie/<int:pk>/offusca', viewsserie.offusca, name='serie-offusca'),
    # sottoserie
    path('serie/<int:pk>/sottoserie', viewssottoserie.SottoSerieListView.as_view(), name='sottoserie-list'),
    path('serie/<int:pk_serie>/sottoserie/add', viewssottoserie.SottoSerieCreateView.as_view(), name='sottoserie-add'),
    path('serie/<int:pk_serie>/sottoserie/<int:pk>', viewssottoserie.SottoSerieUpdateView.as_view(), name='sottoserie-update'),
    path('serie/<int:pk_serie>/sottoserie/<int:pk>/delete', viewssottoserie.SottoSerieDeleteView.as_view(), name='sottoserie-delete'),
    path('serie/<int:pk_serie>/sottoserie/<int:pk>/offusca', viewssottoserie.offusca, name='sottoserie-offusca'),
    
    # test
    path('multiple_file_upload_test', viewstest.multiple_file_upload, name='multiple_file_upload_test'),
]