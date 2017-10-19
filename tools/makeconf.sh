#!/usr/bin/env bash
if [ -z $1 ]; then
    echo "Must specify a template name, e.g. tools/makeconf.sh dev"
    exit 1
fi
rm -f config/*
cp config_templates/$1/* config