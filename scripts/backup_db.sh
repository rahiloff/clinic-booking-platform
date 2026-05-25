#!/bin/bash
# Backup Script for PostgreSQL Database
# To be run via Cron: 0 2 * * * /opt/docbook/scripts/backup_db.sh

set -e

BACKUP_DIR="/opt/docbook/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_CONTAINER="docbook-db-1"
DB_USER="docbook_admin"
DB_NAME="docbook_prod"

echo "Starting database backup at $TIMESTAMP..."

mkdir -p "$BACKUP_DIR"

# Execute pg_dump inside the running container
docker exec -t $DB_CONTAINER pg_dump -U $DB_USER -d $DB_NAME -F c > "$BACKUP_DIR/db_backup_$TIMESTAMP.dump"

# Keep only the last 7 backups to save disk space
ls -t "$BACKUP_DIR"/db_backup_*.dump | tail -n +8 | xargs rm -f --

echo "Backup completed: $BACKUP_DIR/db_backup_$TIMESTAMP.dump"
