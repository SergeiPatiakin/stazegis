#!/usr/bin/env bash
psql -U postgres $POSTGRES_DB < /data/postgres_backup/staze_backup.sql