#!/usr/bin/env bash
certbot certonly --webroot -w /data/letsencrypt_webroot -d $CERTBOT_SITE1 -d $CERTBOT_SITE2