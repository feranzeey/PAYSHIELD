
#!/bin/bash

set -Eeuo pipefail

# PayShield Automated Disaster Recovery Test

BACKUP_FILE="${1:-}"
CONTAINER="payshield-db"
DB_USER="payshield_user"
SOURCE_DB="payshield_db"
TEST_DB="payshield_restore_test"
LOG_DIR="./logs"
LOG_FILE="$LOG_DIR/restore-test.log"

mkdir -p "$LOG_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

cleanup() {
    local exit_code=$?

    if docker exec "$CONTAINER" dropdb \
        -U "$DB_USER" --if-exists "$TEST_DB" >/dev/null 2>&1; then
        log "Temporary database cleanup completed."
    else
        log "WARNING: Temporary database cleanup failed."
        if [ "$exit_code" -eq 0 ]; then
            exit_code=1
        fi
    fi

    if [ "$exit_code" -eq 0 ]; then
        log "Disaster recovery test PASSED."
    else
        log "Disaster recovery test FAILED."
    fi

    exit "$exit_code"
}

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: ./scripts/restore-test.sh <backup-file>"
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ] || [ ! -s "$BACKUP_FILE" ]; then
    echo "ERROR: Backup file does not exist or is empty."
    exit 1
fi

trap cleanup EXIT

log "Starting PayShield disaster recovery test."

docker exec "$CONTAINER" pg_isready -U "$DB_USER"

docker exec "$CONTAINER" dropdb \
    -U "$DB_USER" --if-exists "$TEST_DB"

docker exec "$CONTAINER" createdb \
    -U "$DB_USER" "$TEST_DB"

log "Restoring database backup."

docker exec -i "$CONTAINER" pg_restore \
    -U "$DB_USER" \
    -d "$TEST_DB" \
    --no-owner \
    --no-privileges \
    --exit-on-error \
    < "$BACKUP_FILE"

log "Verifying payment records."

SOURCE_COUNT=$(docker exec "$CONTAINER" psql \
    -U "$DB_USER" -d "$SOURCE_DB" \
    -tAc "SELECT COUNT(*) FROM payments;")

RESTORED_COUNT=$(docker exec "$CONTAINER" psql \
    -U "$DB_USER" -d "$TEST_DB" \
    -tAc "SELECT COUNT(*) FROM payments;")

log "Original payment records: $SOURCE_COUNT"
log "Restored payment records: $RESTORED_COUNT"

if [ "$SOURCE_COUNT" -ne "$RESTORED_COUNT" ]; then
    log "ERROR: Payment counts do not match."
    exit 1
fi

SOURCE_DATA=$(docker exec "$CONTAINER" psql \
    -U "$DB_USER" -d "$SOURCE_DB" \
    -tAc "COPY (
        SELECT reference, amount, currency, description, status, created_at
        FROM payments ORDER BY reference
    ) TO STDOUT WITH CSV")

RESTORED_DATA=$(docker exec "$CONTAINER" psql \
    -U "$DB_USER" -d "$TEST_DB" \
    -tAc "COPY (
        SELECT reference, amount, currency, description, status, created_at
        FROM payments ORDER BY reference
    ) TO STDOUT WITH CSV")

if [ "$SOURCE_DATA" != "$RESTORED_DATA" ]; then
    log "ERROR: Payment data integrity verification failed."
    exit 1
fi

log "SUCCESS: All payment records match exactly."
