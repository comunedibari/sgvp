from datetime import date
from django.http import HttpRequest

from .models import ApiKey, Serie, SottoSerie, UserSeries
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.mixins import UserPassesTestMixin,LoginRequiredMixin

#utente in request    
def user_in_request(request:HttpRequest):
    return request.user

def is_staff_or_superuser(user):
    if user.is_authenticated and (user.is_staff or user.is_superuser):
        return True
    return False

def has_role_on_serie(request:HttpRequest,serie:Serie,roles:list):
    user=user_in_request(request)
    if (not user.is_authenticated):
        return False
    if is_staff_or_superuser(user):
        return True
    #verifico se ha il ruolo di checker sulla serie del Pass
    userSeries=UserSeries.objects \
            .filter(user__username=user.username,ruolo__in=roles,serie=serie) \
            .filter(Q(data_fine_validita__isnull=True)|Q(data_fine_validita__gte=date.today()))\
            .all()
    return userSeries
       

def has_role(request:HttpRequest,role:str):
    user=user_in_request(request)
    if (not user.is_authenticated):
        return False
    if is_staff_or_superuser(user):
        return True
    #verifico se ha il ruolo su almeno una serie ad oggi valido...
    return user_has_role(user.username,role)

def user_roles(username:str,roles:list):
    userSeries=UserSeries.objects\
        .filter(user__username=username,ruolo__in=roles)\
        .filter(Q(data_fine_validita__isnull=True)|Q(data_fine_validita__gte=date.today()))\
        .all()
    return userSeries


def user_role(username:str,role:str):
    userSeries=UserSeries.objects\
        .filter(user__username=username,ruolo=role)\
        .filter(Q(data_fine_validita__isnull=True)|Q(data_fine_validita__gte=date.today()))\
        .all()
    return userSeries

def user_has_role(username:str,role:str):
    userSeries=user_role(username,role)
    return userSeries and len(userSeries)>0

def is_gestore(user):
    return is_staff_or_superuser or user_has_role(user.username,UserSeries.TP_GESTORE)

def user_sotto_series(user:User,roles:list,valid_now:bool):
    if is_staff_or_superuser(user):
        qs=SottoSerie.objects.all()
    else:
        qs=SottoSerie.objects\
            .filter(serie__user_series__user__username=user.username,serie__user_series__ruolo__in=roles)\
            .filter(serie__user_series__data_inizio_validita__lte=date.today())\
            .filter(Q(serie__user_series__data_fine_validita__isnull=True)|Q(serie__user_series__data_fine_validita__gte=date.today())) 
    if valid_now:
        qs=qs.filter(data_inizio_validita__lte=date.today()).filter(Q(data_fine_validita__isnull=True)|Q(data_fine_validita__gte=date.today()))    
    return qs

# restituisce il queryset delle sottoserie
#  attive per l'utente in base al suo ruolo
def user_sotto_series_from_request(request:HttpRequest,roles:list,valid_now:bool):
    """_summary_

    Args:
        request (HttpRequest): _description_
        roles (list): ruoli permessi 
        valid_now (bool): opzionale, se a true filtra le sottoserie valide ad oggi

    Returns:
        _type_: _description_
    """
    user=user_in_request(request)
    if (not user.is_authenticated):
        return SottoSerie.objects.none()
    return user_sotto_series(user=user,roles=roles,valid_now=valid_now)

def user_sotto_series_from_username(username:str,roles:list,valid_now:bool):
    """_summary_

    Args:
        request (HttpRequest): _description_
        roles (list): ruoli permessi 
        valid_now (bool): opzionale, se a true filtra le sottoserie valide ad oggi

    Returns:
        _type_: _description_
    """
    user=User.objects.get(username=username)
    return user_sotto_series(user=user,roles=roles,valid_now=valid_now)
    
class BaseStaffOrSuperuserView(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        # test di accesso
        if is_staff_or_superuser(user_in_request(self.request)):
            return True
        else:
            return False

def has_key_valid(key,sotto_serie_id):
    """true se la key esiste sulla sotto_serie ed è valida ad oggi

    Args:
        key (_type_): _description_
        sotto_serie_id (_type_): _description_

    Returns:
        _type_: _description_
    """
    qs=ApiKey.objects\
            .filter(sotto_serie__id=sotto_serie_id,key=key)\
            .filter(data_inizio_validita__lte=date.today())\
            .filter(Q(data_fine_validita__isnull=True)|Q(data_fine_validita__gte=date.today())) 
    return len(qs)>0
        