# Docker Setup per dja-badge

Questa cartella contiene la configurazione per eseguire l'applicazione dja-badge in un contenitore Docker.

## Requisiti

- Docker Desktop installato e in esecuzione
- Docker Compose (incluso in Docker Desktop)

## File di configurazione

- **Dockerfile**: Immagine Docker con Python 3.14 e tutte le dipendenze necessarie
- **docker-compose.yml**: Configurazione dei servizi e volumi

## Come usare

### Su Linux/macOS
per buildare l'immagine dalla cartella principale del progetto:
docker image build -f docker/Dockerfile -t dja-badge .

## Volumi montati

- **Media files**: `dja_badge_site/media` → `/app/media` (nel container)
- **Static files**: `dja_badge_site/staticfilescollected` → `/app/staticfilecollected` (nel container)


Vedere la documentazione di Django e Docker per best practices di produzione.
