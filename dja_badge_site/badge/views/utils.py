from django.http import HttpRequest

from badge.models import UserSeries
from badge.permission import has_role, is_staff_or_superuser, user_in_request
from badge.utils import get_deleted_objects


def add_role(request:HttpRequest,context):
    """aggiunge nel context is_gestore e is_stf_or_su

    Args:
        request (HttpRequest): _description_
        context (_type_): _description_
    """
    is_gestore=has_role(request=request,role=UserSeries.TP_GESTORE)
    is_stf_or_su=is_staff_or_superuser(user_in_request(request=request))
    context['is_gestore']=is_gestore
    context['is_stf_or_su']=is_stf_or_su


def add_deleted_objects(request:HttpRequest,context,object):
    """aggiunge nel context deletable_objects,model_count,protected

    Args:
        request (HttpRequest): _description_
        context (_type_): 
        object (_type_): Oggetto da cancellare
    """
    #per il popolamento della cancellazione:
    deletable_objects, model_count, protected = get_deleted_objects([object])
    context['deletable_objects']=deletable_objects
    context['model_count']=dict(model_count).items()
    context['protected']=protected
