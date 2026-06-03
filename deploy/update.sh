#!/usr/bin/env bash
# NileGov Stack — pull latest code and restart service
# Run as root (or with sudo) on the Hetzner node.
# Usage: bash update.sh

set -euo pipefail

APP_USER="nilegov"
APP_DIR="/opt/nilegov"
BRANCH="${BRANCH:-main}"

echo "==> Pulling latest code (branch: $BRANCH)"
cd "$APP_DIR"
sudo -u "$APP_USER" git fetch origin
sudo -u "$APP_USER" git reset --hard origin/"$BRANCH"

echo "==> Installing dependencies"
sudo -u "$APP_USER" npm install --workspaces

echo "==> Building"
sudo -u "$APP_USER" npm run build

echo "==> Restarting service"
systemctl restart nilegov
sleep 2
echo "==> Service status: $(systemctl is-active nilegov)"
echo "Done. Logs: journalctl -u nilegov -f"
