#!/usr/bin/env bash
##############################################################################
# NileGov Stack — Let's Encrypt SSL setup
# Run AFTER setup-hetzner.sh, once DNS is pointing to this server.
# Usage: DOMAIN=nilegov.mbarara.go.ug bash deploy/ssl.sh
##############################################################################

set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
step()  { echo -e "\n${GREEN}==>${NC} $*"; }
error() { echo -e "${RED}[✗]${NC} $*"; exit 1; }

[[ $EUID -ne 0 ]] && error "Run as root"
[[ -z "${DOMAIN:-}" ]] && error "Set DOMAIN=your.domain.com before running this script"

APP_DIR="/opt/nilegov"

# ─── 1. Obtain certificate ───────────────────────────────────────────────────
step "Obtaining Let's Encrypt certificate for $DOMAIN"
certbot --nginx \
    --non-interactive \
    --agree-tos \
    --redirect \
    --email "${EMAIL:-webmaster@$DOMAIN}" \
    -d "$DOMAIN"

# ─── 2. Install production nginx config ──────────────────────────────────────
step "Installing HTTPS nginx config"
NGINX_CONF="/etc/nginx/sites-available/nilegov"
cp "$APP_DIR/deploy/nginx.conf" "$NGINX_CONF"
sed -i "s/DOMAIN_PLACEHOLDER/$DOMAIN/g" "$NGINX_CONF"

nginx -t && systemctl reload nginx
echo "  Nginx reloaded with HTTPS config."

# ─── 3. Test auto-renewal ────────────────────────────────────────────────────
step "Testing auto-renewal (dry run)"
certbot renew --dry-run

# ─── 4. Update APP_URL in .env ───────────────────────────────────────────────
ENV_FILE="$APP_DIR/server/.env"
if [[ -f "$ENV_FILE" ]]; then
    # Replace http:// variant if present
    sed -i "s|APP_URL=http://.*|APP_URL=https://$DOMAIN|g" "$ENV_FILE"
    sed -i "s|APP_URL=https://your-domain.com|APP_URL=https://$DOMAIN|g" "$ENV_FILE"
    sed -i "s|PESAPAL_IPN_URL=https://your-domain.com|PESAPAL_IPN_URL=https://$DOMAIN|g" "$ENV_FILE"
    systemctl restart nilegov
    echo "  Updated APP_URL in .env and restarted service."
fi

echo ""
echo -e "${GREEN}HTTPS is live at: https://$DOMAIN${NC}"
echo ""
echo "  Auto-renewal runs via certbot's systemd timer (certbot.timer)."
echo "  Check: systemctl status certbot.timer"
