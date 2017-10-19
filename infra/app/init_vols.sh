#!/usr/bin/env bash
# Set up fake SSL certificates
bash infra/app/certbot_bootstrap.sh
# Run DB migrations
python stazegis/manage.py migrate
# Collect static files
python stazegis/manage.py collectstatic --noinput -c
# Set up Geoserver
python stazegis/manage.py setup_geoserver