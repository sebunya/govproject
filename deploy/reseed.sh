#!/usr/bin/env bash
# Reset to camera-ready demo state (wipes DB and uploads, re-seeds)
# Usage: bash reseed.sh

set -euo pipefail

APP_USER="nilegov"
APP_DIR="/opt/nilegov"

echo "==> Re-seeding NileGov Stack demo database"
sudo -u "$APP_USER" bash -c "cd $APP_DIR && npm run seed"
echo "==> Done. Demo state restored."
