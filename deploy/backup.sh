#!/usr/bin/env bash
##############################################################################
# NileGov Stack — SQLite database backup
# Safe for live systems (uses SQLite .backup command, WAL-safe)
# Set up via cron or systemd timer — see instructions below.
##############################################################################

set -euo pipefail

APP_DIR="/opt/nilegov"
DB_FILE="$APP_DIR/server/data/nilegov.db"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/nilegov}"
KEEP_DAYS="${KEEP_DAYS:-14}"       # days to retain backups
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/nilegov_${TIMESTAMP}.db"

mkdir -p "$BACKUP_DIR"

if [[ ! -f "$DB_FILE" ]]; then
    echo "[backup] Database not found: $DB_FILE" >&2
    exit 1
fi

# Use sqlite3 .backup — WAL-safe online backup
sqlite3 "$DB_FILE" ".backup '$BACKUP_FILE'"
gzip "$BACKUP_FILE"

echo "[backup] Saved: ${BACKUP_FILE}.gz ($(du -sh "${BACKUP_FILE}.gz" | cut -f1))"

# Prune old backups
DELETED=$(find "$BACKUP_DIR" -name "nilegov_*.db.gz" -mtime +"$KEEP_DAYS" -print -delete | wc -l)
[[ "$DELETED" -gt 0 ]] && echo "[backup] Pruned $DELETED backups older than ${KEEP_DAYS} days"

##############################################################################
# To run daily at 02:00 — add this to root's crontab (crontab -e):
#
#   0 2 * * * BACKUP_DIR=/var/backups/nilegov bash /opt/nilegov/deploy/backup.sh >> /var/log/nilegov-backup.log 2>&1
#
# Or as a systemd timer — create /etc/systemd/system/nilegov-backup.service:
#
#   [Unit]
#   Description=NileGov database backup
#   [Service]
#   Type=oneshot
#   ExecStart=bash /opt/nilegov/deploy/backup.sh
#   Environment=BACKUP_DIR=/var/backups/nilegov
#
# And /etc/systemd/system/nilegov-backup.timer:
#
#   [Unit]
#   Description=Daily NileGov backup
#   [Timer]
#   OnCalendar=*-*-* 02:00:00
#   Persistent=true
#   [Install]
#   WantedBy=timers.target
#
# Then: systemctl enable --now nilegov-backup.timer
##############################################################################
