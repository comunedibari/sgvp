# SGVP Bari
Sistema di Gestione e Verifica dei Pass per il Comune di Bari

Il sistema nasce dalla necessità di gestire tramite un portale i pass emessi dall'ente comune utilizzati per il riconoscimento:
- dei veicoli dell’autoparco
- degli operatori dello staff nominato in caso di eventi gestiti dall'ente
- qualsiasi altra collezione di beni o soggetti da identificare 

I Pass generati dal SGVP sono riproducibili su supporto cartaceo ed espongono un QR Code che contiene l’url sul dominio certificato su cui 
vengono pubblicati i dati relativi al Pass.

Il sistema è estremamente flessibile nella definizione del set di dati da associare al Pass, e nella configurazione di stampa dello stesso.
Ogni pass è basato sul censimento di un modello sul quale è possibile definire un numero illimitato di metadati, ogni metadato ha una tipologia tra:
- Stringa
- Testo (anche html)
- Data
- File
- Immagine

e attributi come:

- privato
- stampabile
- obbligatorio

Tra le funzionalità principali del sistema:
- la gestione di eventuali dati personali e la relativa anonimizzazione al termine delle esigenze di trattamento degli stessi
- integrazione con LDAP per autenticazione
- gestione di modelli differenti per ogni collezione definita (serie)
- visualizzazione dell'anteprima del modello definito

L'url codificato nel QR code è parametrizzato in una variabile di environment con il placeholder {badge_id} che indica l'uuid che identifica il Pass.

SGVP è realizzato con le seguenti tecnologie:
- django framework versione 4.1.7 (framework python per lo sviluppo di portali web basato su pattern MVC)
- DBMS: PostgreSQL versione 12, oppure SQLite 
- Bootstrap Italia versione 2.0.9 (integrato nel pacchetto python django-design-theme:2.0.9)
- Altre librerie python per gestione dei PDF e miglioramento del rendering frontend (la lista completa è nel file requirements.txt)

## Struttura del repository

```
├───dja_badge_site            --diango project dir
│   ├───badge                 --pass application django
│   └───static                --static resources
├───docs                      --documentazione aggiuntiva
├───screenshots               --immagini della GUI di SGVP
│   activate_venv.bat         --script per avviare i venv in sistemi Windows
│   activate_venv.sh          --script per avviare i venv in bash  
│   gunicorn_start            --script di esempio di avvio gunicorn in ambiente Linux
└   requirements.txt          --elenco dipendenze python

```
## Prerequisiti
Ambiente python >= 3

## Installazione
- installazione dell'ambiente python >=3 [Python getting started](https://www.python.org/about/gettingstarted/)
- Individuare una cartella dove inserire i sorgenti del progetto (di seguito ROOT_PROJ) e posizionarsi all’interno con il prompt dei comandi
- Clonare questo repository
- Creazione del virtual env di python in modo da isolare le dipendenze python di SGVP dai restanti progetti python installati localmente, nella cartella nominata .venv .
`python -m venv .venv`
- Attivazione della shell del venv creato:
    in caso di sistema operativo linux lanciare:
    `source ./.venv/bin/activate`
- Installazione delle dipendenze di progetto:
`python -m pip install -r requirements.txt`
- Installazione del DMBS PostgreSQL (fare riferimento alla documentazione ufficiale)
- Se si sceglie di utilizzare PostgreSQL:
    - Creazione dell’utenza per l’accesso al DB es: 
    `CREATE ROLE sgvp NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT LOGIN NOREPLICATION NOBYPASSRLS PASSWORD 'sgvp'`
    - Creazione del database per SGVP e assegnazione dell’owner all’utente appena creato
    `CREATE DATABASE sgvp`
- Creazione del file che contiene tutte le variabili di environment es. prod.env e impostazione all’interno delle variabili (l’esempio sottostante si riferisce ad un sistema operativo Linux - like)
```
# prod.env
DJANGO_SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DJANGO_DEBUG=False
DATABASE_URL=postgres://userxxx:passwdxxx@ipdbms:port/dbsgvp
ALLOWED_HOSTS=localhost,127.0.0.1
#url con placeholder che verrà utilizzato per creare l’URL del pass da codificare nel QR code
ORIGIN_URL_PASS_DETAIL=https://urlpubblica/pass/{badge_id}/detail
CSRF_TRUSTED_ORIGINS=https://urlpubblica
ENABLE_LDAP=True
LDAP_AUTH_URL=ldap://hostldap:portldap
LDAP_AUTH_SEARCH_BASE="DC=foo,DC=bar,DC=it"
LDAP_AUTH_ACTIVE_DIRECTORY_DOMAIN=MYCOMUNE
LDAP_AUTH_CONNECTION_USERNAME=userldap
LDAP_AUTH_CONNECTION_PASSWORD="passwordldap"
LDAP_FILTRO_RESTRIZIONE_UTENTI_AUTENTICABILI=

export DJANGO_SECRET_KEY DJANGO_DEBUG DATABASE_URL ALLOWED_HOSTS ORIGIN_URL_PASS_DETAIL CSRF_TRUSTED_ORIGINS ENABLE_LDAP LDAP_AUTH_URL LDAP_AUTH_SEARCH_BASE LDAP_AUTH_ACTIVE_DIRECTORY_DOMAIN LDAP_AUTH_CONNECTION_USERNAME LDAP_AUTH_CONNECTION_PASSWORD LDAP_FILTRO_RESTRIZIONE_UTENTI_AUTENTICABILI
```
- Posizionarsi nella sottocartella dja_badge_site e lanciare il comando di applicazione delle migrazioni DB:
    `python manage.py migrate`
- Creare l’utente superuser: 
    `python manage.py createsuperuser`
- Per avviare il server lanciare `python manage.py runserver`, ol portale è disponibile all’url `http://localhost:8000/`

## Status del progetto
Il progetto è in versione stabile

## Know Issues
- rendering dei metadati in formato HTML non implementato

## Copyright
- Detentore del copyright: Comune di Bari 
- Mantainers: 
  - Francesco Valle <f.valle@comune.bari.it>
  - Vito Ciocia <v.ciocia@comune.bari.it> 
  - Adriano Colaianni <adriano.colaianni@comune.bari.it>
- Per segnalazioni sulla sicurezza contattare via mail: <privacy@comune.bari.it>

## 📄 License
Il software è rilasciato con licenza:
European Union Public License 1.2
Dettagli nel file [LICENSE](LICENSE)

## screenshots
![Screenshot](screenshots/sgvp.gif)

