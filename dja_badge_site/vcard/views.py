from django.shortcuts import get_object_or_404, redirect, render
from uuid import UUID
from django.http import HttpResponse
from .models import VCard

# Visualizza vcard per id
def vcard_by_id(request, vcard_id:UUID):
    vcardObj = get_object_or_404(VCard, pk=vcard_id)
    
    return render(request, 'vcard/index.html', {
        'vcard': vcardObj,
    })

# Genera il file vcf al click dell'utente
def generate_vcf(request, vcard_id:UUID):
    vcardObj = get_object_or_404(VCard, pk=vcard_id)
    vcf_content = generate_vcf_file(vcardObj)  # Supponiamo che questa funzione crei il contenuto VCF
    
    response = HttpResponse(vcf_content, content_type='text/vcard')
    response['Content-Disposition'] = f'attachment; filename="{vcardObj.nome}_{vcardObj.cognome}.vcf"'
    
    return response

def generate_vcf_file(vcard):
    vcf = f"BEGIN:VCARD\nVERSION:3.0\n"
    
    # Aggiungi nome e cognome
    vcf += f"FN:{vcard.nome} {vcard.cognome}\n"
    vcf += f"N:{vcard.cognome};{vcard.nome};;;\n"  # Ordine cognome, nome per il campo 'N'
    
    # Aggiungi titolo se presente
    if vcard.titolo:
        vcf += f"TITLE:{vcard.organizzazione} - {vcard.ufficio}\n"
    
    # Aggiungi profilo
    if vcard.profilo:
        vcf += f"ROLE:{vcard.profilo}\n"
    
    # Aggiungi ufficio
    if vcard.organizzazione:
        vcf += f"ORG:{vcard.organizzazione}\n"
    
    # Aggiungi indirizzo ufficio
    if vcard.indirizzo_ufficio:
        vcf += f"ADR;TYPE=work:;;{vcard.indirizzo_ufficio}\n"
    
    # Aggiungi telefono fisso se presente
    if vcard.telefono_fisso:
        vcf += f"TEL;TYPE=work:{vcard.telefono_fisso}\n"
    
    # Aggiungi telefono cellulare se presente
    if vcard.telefono_cellulare:
        vcf += f"TEL;TYPE=cell:{vcard.telefono_cellulare}\n"
    
    # Aggiungi email se presente
    if vcard.email:
        vcf += f"EMAIL:{vcard.email}\n"
    
    vcf += "END:VCARD"
    
    return vcf
