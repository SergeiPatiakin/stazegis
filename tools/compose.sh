#!/usr/bin/env bash
docker-compose -f docker-compose-base.yml -f config/docker-compose-custom.yml "$@"