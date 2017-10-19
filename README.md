# Features

Stazegis is a project showing how to build an interactive map application using Django, Postgis, Geoserver and OpenLayers:
  
 - Geolocation API to display current location
 - History API to encode map state in URL
 - GPX file import via ogr2ogr
 - Custom Django user model for email/password login
 - Automatic geoserver setup via REST API
 - Let's Encrypt SSL certificates with automatic renewal
 - Docker and docker-compose for full containerization.
 

# Quick start
 - `tools/makeconf.sh dev`
 - `tools/compose.sh up -d`
 - (wait 20 seconds for container to start up)
 - `tools/initialize.sh`

# Populating test data
 - `tools/compose.sh exec app python stazegis/manage.py loaddata articles.json`

# Tools
 ## tools/makeconf.sh
   Copy configuration files from a template directory to the active configuration directory.
     
     # Copy configuration from dev template
     tools/makeconf.sh dev
     # Copy configuration from prod template
     tools/makeconf.sh prod
    
 ## tools/compose.sh
   Wrapper around `docker-compose` that defines the configuration files (-f parameter). All arguments are passed 
   straight through to `docker-compose`.
     
     # Bring up all containers
     tools/compose.sh up -d
     
     # Stop nginx
     tools/compose.sh stop nginx
     
     # Get shell in app container
     tools/compose.sh exec app bash
 
 ## tools/initialize.sh
   Initialize the app. Perform migrations, collect static files, set up fake SSL certificates.
   Requires the `app` and `db` containers to be up.
 
 ## tools/db_backup.sh
   Backup database to the `postgres_backup` named volume.
   Requires the `db` container to be up.
  
 ## tools/db_restore.sh
   Restore database from the `postgres_backup` named volume.
   Requires the `db` container to be up.
