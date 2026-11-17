#!/bin/bash

set -euo pipefail

# PayShield PostgreSQL Backup Script

BACKUP_DIR="./backups"
CONTAINER="payshield-db"
DB_USER="payshield_user"
DB_NAME="payshield_db"
RETENTION_DAYS=7

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/payshield_${TIMESTAMP}.dump"

echo "Starting PayShield database backup..."

mkdir -p "$BACKUP_DIR"

# Create PostgreSQL backup
if ! docker exec "$CONTAINER" pg_dump \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    -Fc > "$BACKUP_FILE"; then
    echo "ERROR: Database backup failed."
    rm -f "$BACKUP_FILE"
    exit 1
fi

# Check backup file
if [ ! -s "$BACKUP_FILE" ]; then
    echo "ERROR: Backup file is empty."
    rm -f "$BACKUP_FILE"
    exit 1
fi

# Validate backup
if ! docker exec -i "$CONTAINER" pg_restore \
    --list < "$BACKUP_FILE" > /dev/null; then
    echo "ERROR: Backup validation failed."
    rm -f "$BACKUP_FILE"
    exit 1
fi

echo "Backup completed successfully!"
echo "Backup location: $BACKUP_FILE"
echo "Backup size: $(du -h "$BACKUP_FILE" | cut -f1)"

# Remove timestamped backups older than 7 days
echo "Applying backup retention policy..."

find "$BACKUP_DIR" \
    -maxdepth 1 \
    -type f \
    -name 'payshield_????????_??????.dump' \
    -mtime +"$RETENTION_DAYS" \
    -print -delete

echo "Backup retention policy completed."
