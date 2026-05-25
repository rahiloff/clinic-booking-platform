#!/bin/bash
# Restore Script for PostgreSQL Database
# Usage: ./scripts/restore_db.sh <path_to_backup_file>

set -e

if [ -z "$1" ]; then
  echo "Error: Please provide the path to the backup file."
  echo "Usage: ./scripts/restore_db.sh backups/db_backup_2024...dump"
  exit 1
fi

BACKUP_FILE=$1
DB_CONTAINER="docbook-db-1"
DB_USER="docbook_admin"
DB_NAME="docbook_prod"

echo "Restoring database from $BACKUP_FILE..."

# Drop existing connections and database
docker exec -it $DB_CONTAINER psql -U $DB_USER -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME';"
docker exec -it $DB_CONTAINER psql -U $DB_USER -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"
docker exec -it $DB_CONTAINER psql -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME;"

# Restore the dump file
docker exec -i $DB_CONTAINER pg_restore -U $DB_USER -d $DB_NAME -1 < "$BACKUP_FILE"

echo "Database restore completed successfully."
