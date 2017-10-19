#!/usr/bin/env bash
# Certbot insists on placing certs/keys in this directory
CERTBOT_SITE_DIR=/etc/letsencrypt/live/$CERTBOT_SITE1
mkdir -p $CERTBOT_SITE_DIR
# Create a symlink for nginx to use. This way we avoid parameterizing the nginx config
ln -s $CERTBOT_SITE_DIR /etc/letsencrypt/live_site_dir
# Create symlinks to our fake certs, so that nginx can start
ln -s /code/infra/ssl/fake_certificate.pem $CERTBOT_SITE_DIR/fullchain.pem
ln -s /code/infra/ssl/fake_key.pem $CERTBOT_SITE_DIR/privkey.pem