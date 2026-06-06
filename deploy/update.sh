#!/usr/bin/env bash
##############################################################################
# NileGov Stack — pull latest code and redeploy (zero-downtime build)
# Run as root on the Hetzner node.
# Usage: bash /opt/nilegov/deploy/update.sh
##############################################################################

set -euo pipefail

APP_USER="nilegov"
APP_DIR="/opt/nilegov"
BRANCH="${BRANCH:-main}"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
step() { echo -e "\n${GREEN}==>${NC} $*"; }
warn() { echo -e "${YELLOW}[!]${NC} $*"; }

step "Pulling latest code (branch: $BRANCH)"
cd "$APP_DIR"
sudo -u "$APP_USER" git fetch origin
sudo -u "$APP_USER" git reset --hard origin/"$BRANCH"
echo "  HEAD: $(git rev-parse --short HEAD) — $(git log -1 --format='%s')"

step "Installing dependencies"
sudo -u "$APP_USER" npm install --workspaces --include=dev

step "Building client and server"
sudo -u "$APP_USER" bash -c "cd $APP_DIR && npm run build"

step "Restarting service"
systemctl restart nilegov
sleep 2
STATUS=$(systemctl is-active nilegov)
echo "  Service: $STATUS"
[[ "$STATUS" != "active" ]] && { journalctl -u nilegov --no-pager -n 30; exit 1; }

step "Reloading nginx"
nginx -t && systemctl reload nginx

echo ""
echo -e "${GREEN}Update complete.${NC} Logs: journalctl -u nilegov -f"
warn "Run 'bash $APP_DIR/deploy/reseed.sh' if schema changed and you need fresh demo data."
