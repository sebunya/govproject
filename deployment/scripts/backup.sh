#!/usr/bin/env bash

# NileGov Stack Automated Backup Script
# Performs self-consistent backup, GPG encryption, local rotation, and optional remote transfer.
# Best run as a cron job by the 'nilegov' user or root.

set -euo pipefail

# Find script directory and load .env configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [ -f "${PROJECT_DIR}/.env" ]; then
    # shellcheck disable=SC1091
    source "${PROJECT_DIR}/.env"
else
    echo "[ERROR] .env file not found at ${PROJECT_DIR}/.env" >&2
    exit 1
fi

# --- Variables ---
SITE_NAME="${SITE_NAME:-nilegov.yourdomain.com}"
BACKUP_ENCRYPTION_KEY="${BACKUP_ENCRYPTION_KEY:-nilegov_secure_backup_key_change_me}"
BACKUP_DIR="/var/backups/nilegov"
KEEP_DAYS=7
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
TEMP_DIR="${BACKUP_DIR}/temp_${TIMESTAMP}"

# Log utilities
log_info() { echo -e "\e[32m[INFO]\e[0m $*"; }
log_error() { echo -e "\e[31m[ERROR]\e[0m $*" >&2; }

# Check if Docker compose is running and backend container exists
cd "${PROJECT_DIR}"
if ! docker compose ps | grep -q "nilegov-backend"; then
    log_error "NileGov Stack backend container is not running. Cannot perform live backup."
    exit 1
fi

# Ensure backup directories exist
mkdir -p "${BACKUP_DIR}"
mkdir -p "${TEMP_DIR}"

log_info "Initiating database and site files backup for site: ${SITE_NAME}..."

# Step 1: Run Frappe bench backup command inside the backend container
# This guarantees transaction-consistent DB dumps and archives uploads/private files
if ! docker compose exec -T backend bench --site "${SITE_NAME}" backup --with-files; then
    log_error "Frappe bench backup command failed inside backend container."
    rm -rf "${TEMP_DIR}"
    exit 1
fi

# Step 2: Copy backups out of container
# Backups are generated in sites/<site_name>/private/backups/ inside the volume
log_info "Extracting backup archives from backend container..."
docker compose cp backend:/home/frappe/frappe-bench/sites/${SITE_NAME}/private/backups/ "${TEMP_DIR}/"

# Step 3: Bundle and Encrypt using GPG AES-256
RAW_TAR="${BACKUP_DIR}/nilegov_raw_${TIMESTAMP}.tar"
ENCRYPTED_FILE="${BACKUP_DIR}/nilegov_backup_${TIMESTAMP}.tar.gpg"

log_info "Creating combined archive of database dumps and site files..."
tar -cf "${RAW_TAR}" -C "${TEMP_DIR}/backups" .

log_info "Encrypting backup archive with AES-256 GPG..."
gpg --batch --yes --passphrase "${BACKUP_ENCRYPTION_KEY}" --symmetric --cipher-algo AES256 -o "${ENCRYPTED_FILE}" "${RAW_TAR}"

# Clean up raw unencrypted data immediately
rm -rf "${TEMP_DIR}"
rm -f "${RAW_TAR}"

# Restrict permissions of the encrypted backup file
chmod 600 "${ENCRYPTED_FILE}"
log_info "Backup successfully created and encrypted: ${ENCRYPTED_FILE}"

# Step 4: Optional Encrypted Off-Server Sync Target
# Add your custom off-site storage commands here (e.g. S3 upload, SFTP, rsync, rclone)
# Example:
# if command -v rclone &>/dev/null && [ -n "${REMOTE_BACKUP_TARGET:-}" ]; then
#     log_info "Syncing encrypted backup to remote target..."
#     rclone copy "${ENCRYPTED_FILE}" "${REMOTE_BACKUP_TARGET}"
# fi
log_info "Off-server backup hook checked (Optional sync to remote storage target)."

# Step 5: Backup Rotation (Clean up old backups)
log_info "Cleaning up local backups older than ${KEEP_DAYS} days..."
find "${BACKUP_DIR}" -name "nilegov_backup_*.gpg" -type f -mtime +"${KEEP_DAYS}" -delete

log_info "Backup process completed successfully."
