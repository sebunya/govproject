#!/usr/bin/env bash

# NileGov Stack Recovery and Restore Script
# Restores database and attachment files from a GPG-encrypted backup file.
# Usage: ./restore.sh /path/to/nilegov_backup_YYYYMMDD_HHMMSS.tar.gpg

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
BACKUP_FILE="${1:-}"

# Log utilities
log_info() { echo -e "\e[32m[INFO]\e[0m $*"; }
log_warn() { echo -e "\e[33m[WARN]\e[0m $*"; }
log_error() { echo -e "\e[31m[ERROR]\e[0m $*" >&2; }

# Step 0: Validate Input
if [ -z "${BACKUP_FILE}" ]; then
    log_error "Usage: $0 /path/to/nilegov_backup_file.tar.gpg"
    exit 1
fi

if [ ! -f "${BACKUP_FILE}" ]; then
    log_error "Backup file not found: ${BACKUP_FILE}"
    exit 1
fi

# Confirm with administrator
log_warn "WARNING: This recovery script will overwrite the active database and files for site: ${SITE_NAME}."
read -p "Are you absolutely sure you want to proceed? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "Restore operation cancelled by user."
    exit 0
fi

# Verify stack containers are active
cd "${PROJECT_DIR}"
if ! docker compose ps | grep -q "nilegov-backend"; then
    log_info "Starting containers to perform recovery..."
    docker compose up -d
    sleep 5
fi

# Create host temporary workspace
HOST_TEMP="/tmp/nilegov_restore_$(date +%s)"
mkdir -p "${HOST_TEMP}"
RAW_TAR="${HOST_TEMP}/raw_backup.tar"

# Step 1: Decrypt GPG backup file
log_info "Decrypting backup file using GPG..."
if ! gpg --batch --yes --passphrase "${BACKUP_ENCRYPTION_KEY}" --decrypt "${BACKUP_FILE}" > "${RAW_TAR}"; then
    log_error "Decryption failed. Please check the encryption key/passphrase."
    rm -rf "${HOST_TEMP}"
    exit 1
fi

# Step 2: Extract decrypted tarball to locate database and files
log_info "Extracting raw backup files..."
mkdir -p "${HOST_TEMP}/extracted"
tar -xf "${RAW_TAR}" -C "${HOST_TEMP}/extracted"

# Find files inside extracted archive
# Bench backup files are named like:
# [timestamp]-[sitename]-site_database.sql.gz
# [timestamp]-[sitename]-files.tar (public files)
# [timestamp]-[sitename]-private_files.tar (private files)
SQL_FILE=$(find "${HOST_TEMP}/extracted" -name "*site_database.sql.gz" | head -n 1)
PUBLIC_FILES=$(find "${HOST_TEMP}/extracted" -name "*files.tar" -not -name "*private_files.tar" | head -n 1)
PRIVATE_FILES=$(find "${HOST_TEMP}/extracted" -name "*private_files.tar" | head -n 1)

if [ -z "${SQL_FILE}" ]; then
    log_error "No database SQL dump (*site_database.sql.gz) found inside the backup."
    rm -rf "${HOST_TEMP}"
    exit 1
fi

log_info "Backup components found:"
log_info "  - DB Dump: $(basename "${SQL_FILE}")"
[ -n "${PUBLIC_FILES}" ] && log_info "  - Public Files: $(basename "${PUBLIC_FILES}")"
[ -n "${PRIVATE_FILES}" ] && log_info "  - Private Files: $(basename "${PRIVATE_FILES}")"

# Step 3: Copy backup files to the backend container
log_info "Copying files to container restoration directory..."
CONTAINER_RESTORE_DIR="/home/frappe/frappe-bench/sites/restore_temp"
docker compose exec -T backend mkdir -p "${CONTAINER_RESTORE_DIR}"

docker compose cp "${SQL_FILE}" "backend:${CONTAINER_RESTORE_DIR}/database.sql.gz"
[ -n "${PUBLIC_FILES}" ] && docker compose cp "${PUBLIC_FILES}" "backend:${CONTAINER_RESTORE_DIR}/public_files.tar"
[ -n "${PRIVATE_FILES}" ] && docker compose cp "${PRIVATE_FILES}" "backend:${CONTAINER_RESTORE_DIR}/private_files.tar"

# Step 4: Run bench restore command inside the backend container
log_info "Running Frappe bench restore command..."
RESTORE_CMD="bench restore ${SITE_NAME} ${CONTAINER_RESTORE_DIR}/database.sql.gz"
[ -n "${PUBLIC_FILES}" ] && RESTORE_CMD="${RESTORE_CMD} --with-public-files ${CONTAINER_RESTORE_DIR}/public_files.tar"
[ -n "${PRIVATE_FILES}" ] && RESTORE_CMD="${RESTORE_CMD} --with-private-files ${CONTAINER_RESTORE_DIR}/private_files.tar"

# Run the command with database configuration parameters
# We append --mariadb-root-password to allow user creation if needed
if ! docker compose exec -T backend bash -c "${RESTORE_CMD} --db-root-username root --db-root-password ${DB_ROOT_PASSWORD:-nilegov_root_pass}"; then
    log_error "Bench restore command failed."
    # Clean up temp files inside container
    docker compose exec -T backend rm -rf "${CONTAINER_RESTORE_DIR}"
    rm -rf "${HOST_TEMP}"
    exit 1
fi

# Step 5: Run DB migration & clean caches to synchronize schemas
log_info "Running bench site migrations and clearing caches..."
docker compose exec -T backend bench --site "${SITE_NAME}" migrate
docker compose exec -T backend bench --site "${SITE_NAME}" clear-cache

# Step 6: Cleanup temporary files on Host and Container
log_info "Cleaning up temporary files..."
docker compose exec -T backend rm -rf "${CONTAINER_RESTORE_DIR}"
rm -rf "${HOST_TEMP}"

log_info "========================================================="
log_info " NileGov Stack Restore & Recovery Completed Successfully! "
log_info "========================================================="
