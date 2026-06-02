#!/usr/bin/env bash

# NileGov Stack System Healthcheck Script
# Verifies container statuses, host resources (disk/RAM), and application endpoints.
# Returns 0 if healthy, 1 if any check fails.

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
MAX_DISK_USAGE_PCT=85
MAX_RAM_USAGE_PCT=90
LOG_FILE="/var/log/nilegov_healthcheck.log"

# Setup logging
mkdir -p "$(dirname "${LOG_FILE}")"
touch "${LOG_FILE}"

log_check() {
    local status="$1"
    local message="$2"
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    if [ "$status" = "OK" ]; then
        echo -e "${timestamp} [OK] ${message}"
        echo "${timestamp} [OK] ${message}" >> "${LOG_FILE}"
    else
        echo -e "\e[31m${timestamp} [FAIL] ${message}\e[0m" >&2
        echo "${timestamp} [FAIL] ${message}" >> "${LOG_FILE}"
        return 1
    fi
}

log_info() {
    local message="$1"
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    echo "${timestamp} [INFO] ${message}" >> "${LOG_FILE}"
}

log_info "Initiating system health check..."
HEALTHY=0

# Check 1: Host Disk Space
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "${DISK_USAGE}" -gt "${MAX_DISK_USAGE_PCT}" ]; then
    log_check "FAIL" "Disk usage is critically high: ${DISK_USAGE}% (limit: ${MAX_DISK_USAGE_PCT}%)" || HEALTHY=1
else
    log_check "OK" "Disk usage is normal: ${DISK_USAGE}%"
fi

# Check 2: Host RAM Usage
RAM_USAGE_PCT=$(free | grep Mem | awk '{print $3/$2 * 100.0}' | cut -d. -f1)
if [ "${RAM_USAGE_PCT}" -gt "${MAX_RAM_USAGE_PCT}" ]; then
    log_check "FAIL" "RAM usage is critically high: ${RAM_USAGE_PCT}% (limit: ${MAX_RAM_USAGE_PCT}%)" || HEALTHY=1
else
    log_check "OK" "RAM usage is normal: ${RAM_USAGE_PCT}%"
fi

# Check 3: Docker Containers Status
cd "${PROJECT_DIR}"
REQUIRED_CONTAINERS=(
    "nilegov-db"
    "nilegov-redis-cache"
    "nilegov-redis-queue"
    "nilegov-backend"
    "nilegov-websocket"
    "nilegov-worker"
    "nilegov-scheduler"
)

for container in "${REQUIRED_CONTAINERS[@]}"; do
    if ! docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        log_check "FAIL" "Container '${container}' is not running!" || HEALTHY=1
        continue
    fi
    
    # Check if container is healthy (if it has a healthcheck defined)
    if docker inspect --format='{{json .State.Health}}' "${container}" | grep -q "status"; then
        STATUS=$(docker inspect --format='{{.State.Health.Status}}' "${container}")
        if [ "${STATUS}" != "healthy" ]; then
            log_check "FAIL" "Container '${container}' is running but reporting state: ${STATUS}" || HEALTHY=1
        else
            log_check "OK" "Container '${container}' is running and healthy."
        fi
    else
        log_check "OK" "Container '${container}' is running."
    fi
done

# Check 4: Web Application Endpoint HTTP Check
# We query localhost on port 8000 (backend direct) and check the HTTP status code.
# Port 8000 is exposed to localhost on the host.
if HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 http://127.0.0.1:8000); then
    # Frappe backend returns 200, 301, 302 or 404 (for root depending on site setup)
    # A status of 000 means Nginx failed to reach the upstream container.
    if [ "${HTTP_STATUS}" -eq 000 ]; then
        log_check "FAIL" "Web backend is unreachable on port 8000" || HEALTHY=1
    elif [ "${HTTP_STATUS}" -ge 500 ]; then
        log_check "FAIL" "Web backend returned server error status code: ${HTTP_STATUS}" || HEALTHY=1
    else
        log_check "OK" "Web backend direct port 8000 is responsive. HTTP status: ${HTTP_STATUS}"
    fi
else
    log_check "FAIL" "Failed to connect to web backend port 8000" || HEALTHY=1
fi

# Summary
if [ "${HEALTHY}" -eq 0 ]; then
    log_info "All services are running normally. Health check: PASSED."
    exit 0
else
    log_info "Some checks failed. Health check: FAILED."
    exit 1
fi
