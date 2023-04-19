# libreria di utilità 
import logging
import os
from django_python3_ldap.utils import format_search_filters

logger = logging.getLogger(__name__)


def custom_format_search_filters(ldap_fields):
    """filtro per restringere l'accesso agli utenti che si possono autenticare tramite LDAP
    preso da variabile di environment LDAP_FILTRO_RESTRIZIONE_UTENTI_AUTENTICABILI
    Args:
        ldap_fields (_type_): _description_

    Returns:
        _type_: _description_
    """
    # Call the base format callable.
    search_filters = format_search_filters(ldap_fields)
    # Advanced: apply custom LDAP filter logic.
    filtro_restrizioni=os.environ.get('LDAP_FILTRO_RESTRIZIONE_UTENTI_AUTENTICABILI','')
    if len(filtro_restrizioni)>0:
        logger.info("applicando il filtro:  "+filtro_restrizioni)
        search_filters.append(filtro_restrizioni)
    # All done!
    return search_filters
