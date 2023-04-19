from django.http import FileResponse
from django.shortcuts import get_object_or_404

from ..permission import has_role, has_role_on_serie, is_staff_or_superuser, user_in_request
from django.contrib.auth.decorators import user_passes_test
from ..models import Badge, MetadatoModelloBadge,MetadatoBadge, ModelloStampaBadge,UserSeries
from django.core.exceptions import PermissionDenied
# Create your views here.

def metadato(request,metadato_id,file_name):
    is_gestore=has_role(request=request,role=UserSeries.TP_GESTORE)
    is_stf_or_su=is_staff_or_superuser(user_in_request(request=request))
    metadatoBadge = get_object_or_404(MetadatoBadge, pk=metadato_id)
    badgeObj = get_object_or_404(Badge, pk=metadatoBadge.badge.id)
    has_bvr=has_role_on_serie(request,serie=badgeObj.sotto_serie.serie,roles=[UserSeries.TP_CHECKER])
    if is_gestore or is_stf_or_su or has_bvr:
        if metadatoBadge.metadato.tipo_metadato==MetadatoModelloBadge.TP_IMAGE:
            return FileResponse(metadatoBadge.valore_image.file,filename=file_name)    
        else:
            return FileResponse(metadatoBadge.valore_file.file,filename=file_name)    
    else:
        raise PermissionDenied    

@user_passes_test(is_staff_or_superuser)
def sfondo_file(request,modello_id,file_name):
    is_stf_or_su=is_staff_or_superuser(user_in_request(request=request))
    modelloStampaObj = get_object_or_404(ModelloStampaBadge, pk=modello_id)
    if is_stf_or_su:
        return FileResponse(modelloStampaObj.file_sfondo.file,filename=file_name)    
        
    else:
        raise PermissionDenied    


        