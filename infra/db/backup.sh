#!/usr/bin/env bash
# Overwritable backup file (will be overwritten on next backup)
pg_dump -U postgres $POSTGRES_DB > /data/postgres_backup/staze_backup.sql
# Non-overwritable backup file (will not be overwritten)
cp /data/postgres_backup/staze_backup.sql /data/postgres_backup/staze_backup_`date -Isecond`