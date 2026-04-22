#!/usr/bin/env bash
# Take a consistent snapshot of the shortlink SQLite database.
#
# Uses `sqlite3 .backup` rather than `cp`, so an in-flight writer cannot
# corrupt the snapshot. Intended to be invoked from a systemd timer or
# a cron entry like:
#
#   0 4 * * *  /opt/shortlink/deploy/backup.sh

set -euo pipefail

DB_PATH="${SHORTLINK_DB_PATH:-/var/lib/shortlink/db.sqlite}"
BACKUP_DIR="${SHORTLINK_BACKUP_DIR:-/var/backups/shortlink}"
RETENTION_DAYS="${SHORTLINK_BACKUP_RETENTION_DAYS:-14}"

if [[ ! -f "$DB_PATH" ]]; then
    echo "shortlink backup: $DB_PATH does not exist" >&2
    exit 1
fi

mkdir -p "$BACKUP_DIR"
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
out="$BACKUP_DIR/shortlink-${timestamp}.sqlite"

sqlite3 "$DB_PATH" ".backup '$out'"
gzip -9 "$out"

# Prune anything older than the retention window.
find "$BACKUP_DIR" -maxdepth 1 -type f -name 'shortlink-*.sqlite.gz' \
    -mtime "+${RETENTION_DAYS}" -delete

echo "shortlink backup: wrote ${out}.gz"
