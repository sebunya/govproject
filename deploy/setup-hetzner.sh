#!/usr/bin/env bash
##############################################################################
# NileGov Stack — Hetzner VPS first-time setup
# Tested on: Ubuntu 22.04 LTS / 24.04 LTS
# Run as root on a fresh server:
#   DOMAIN=nilegov.example.com bash deploy/setup-hetzner.sh
##############################################################################

set -euo pipefail

APP_USER="nilegov"
APP_DIR="/opt/nilegov"
NODE_VERSION="22"
REPO_URL="${REPO_URL:-https://github.com/sebunya/govproject.git}"
BRANCH="${BRANCH:-main}"
DOMAIN="${DOMAIN:-}"          # e.g. nilegov.mbarara.go.ug  (leave empty for IP-only)

# ─── Colour helpers ──────────────────────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
step()  { echo -e "\n${GREEN}==>${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
error() { echo -e "${RED}[✗]${NC} $*"; exit 1; }

[[ $EUID -ne 0 ]] && error "Run this script as root (sudo or su -)"

# ─── 1. System packages ──────────────────────────────────────────────────────
step "Updating system and installing packages"
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    curl git nginx ufw certbot python3-certbot-nginx \
    logrotate unattended-upgrades

# ─── 2. Firewall ─────────────────────────────────────────────────────────────
step "Configuring UFW firewall"
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow OpenSSH
ufw allow 'Nginx Full'       # ports 80 + 443
ufw --force enable
ufw status

# ─── 3. Node.js 22 ───────────────────────────────────────────────────────────
step "Installing Node.js $NODE_VERSION"
if ! command -v node &>/dev/null || [[ "$(node -e 'process.stdout.write(process.version.split(".")[0].slice(1))')" -lt "$NODE_VERSION" ]]; then
    curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash -
    apt-get install -y -qq nodejs
fi
echo "  node $(node -v)  |  npm $(npm -v)"

# ─── 4. App user ─────────────────────────────────────────────────────────────
step "Creating app user: $APP_USER"
id "$APP_USER" &>/dev/null || useradd -r -m -s /bin/bash "$APP_USER"

# ─── 5. Clone repository ─────────────────────────────────────────────────────
step "Cloning repository (branch: $BRANCH)"
rm -rf "$APP_DIR"
git clone --branch "$BRANCH" --depth 1 "$REPO_URL" "$APP_DIR"
chown -R "$APP_USER":"$APP_USER" "$APP_DIR"

# ─── 6. Data directories ─────────────────────────────────────────────────────
step "Creating data directories"
mkdir -p "$APP_DIR/server/data/uploads"
chown -R "$APP_USER":"$APP_USER" "$APP_DIR/server/data"
chmod 750 "$APP_DIR/server/data"

# ─── 7. Environment file ─────────────────────────────────────────────────────
step "Setting up environment config"
ENV_FILE="$APP_DIR/server/.env"
if [[ ! -f "$ENV_FILE" ]]; then
    cp "$APP_DIR/server/.env.example" "$ENV_FILE"
    [[ -n "$DOMAIN" ]] && sed -i "s|https://your-domain.com|https://$DOMAIN|g" "$ENV_FILE"
    chmod 640 "$ENV_FILE"
    chown "$APP_USER":"$APP_USER" "$ENV_FILE"
    warn "Environment file created at $ENV_FILE — fill in real API keys before going live."
else
    echo "  Existing .env preserved."
fi

# ─── 8. Install dependencies ─────────────────────────────────────────────────
step "Installing npm dependencies"
cd "$APP_DIR"
sudo -u "$APP_USER" npm install --workspaces --include=dev

# ─── 9. Build ────────────────────────────────────────────────────────────────
step "Building client (Vite) and server (TypeScript)"
# Client first (independent), then server TypeScript compile
sudo -u "$APP_USER" bash -c "cd $APP_DIR && npm run build"

# ─── 10. Seed demo database ──────────────────────────────────────────────────
step "Seeding demo database"
sudo -u "$APP_USER" bash -c "cd $APP_DIR && npm run seed"

# ─── 11. Systemd service ─────────────────────────────────────────────────────
step "Writing systemd service"
cat > /etc/systemd/system/nilegov.service <<UNIT
[Unit]
Description=NileGov Stack — API Server
Documentation=https://github.com/sebunya/govproject
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
EnvironmentFile=$APP_DIR/server/.env
Environment=NODE_ENV=production
Environment=PORT=3001
Environment=NODE_OPTIONS=--experimental-sqlite
ExecStart=/usr/bin/node $APP_DIR/server/dist/index.js
Restart=on-failure
RestartSec=5
StartLimitInterval=60
StartLimitBurst=3
StandardOutput=journal
StandardError=journal
SyslogIdentifier=nilegov
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ReadWritePaths=$APP_DIR/server/data

[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable nilegov
systemctl restart nilegov
sleep 2
STATUS=$(systemctl is-active nilegov)
echo "  Service status: $STATUS"
[[ "$STATUS" != "active" ]] && { journalctl -u nilegov --no-pager -n 30; error "Service failed to start"; }

# ─── 12. Nginx ───────────────────────────────────────────────────────────────
step "Configuring Nginx"
NGINX_AVAIL="/etc/nginx/sites-available/nilegov"
NGINX_ENABLED="/etc/nginx/sites-enabled/nilegov"

# Use HTTP-only config initially; ssl.sh upgrades to HTTPS
cp "$APP_DIR/deploy/nginx-http.conf" "$NGINX_AVAIL"

# If domain is provided, set server_name
if [[ -n "$DOMAIN" ]]; then
    sed -i "s/server_name _;/server_name $DOMAIN;/" "$NGINX_AVAIL"
fi

ln -sf "$NGINX_AVAIL" "$NGINX_ENABLED"
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# ─── 13. Log rotation ────────────────────────────────────────────────────────
step "Configuring log rotation"
cat > /etc/logrotate.d/nilegov <<LOGROTATE
/var/log/nginx/nilegov_*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    sharedscripts
    postrotate
        /usr/bin/nginx -s reopen
    endscript
}
LOGROTATE

# ─── 14. Automated security updates ──────────────────────────────────────────
step "Enabling unattended security updates"
cat > /etc/apt/apt.conf.d/20nilegov-auto-upgrades <<APT
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
APT::Periodic::AutocleanInterval "7";
APT
systemctl enable unattended-upgrades --quiet

# ─── Done ────────────────────────────────────────────────────────────────────
IP=$(curl -4 -sf ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  NileGov Stack is live!                                  ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  URL            : ${YELLOW}http://${DOMAIN:-$IP}${NC}"
echo -e "  Citizen portal : http://${DOMAIN:-$IP}/"
echo -e "  Officer desk   : http://${DOMAIN:-$IP}/desk?persona=officer"
echo -e "  Supervisor     : http://${DOMAIN:-$IP}/supervisor?persona=supervisor"
echo -e "  Leadership     : http://${DOMAIN:-$IP}/dashboard?persona=leadership"
echo ""
echo -e "  Logs           : ${YELLOW}journalctl -u nilegov -f${NC}"
echo -e "  Re-seed demo   : ${YELLOW}bash $APP_DIR/deploy/reseed.sh${NC}"
echo ""
if [[ -n "$DOMAIN" ]]; then
    echo -e "  ${YELLOW}Next step — enable HTTPS:${NC}"
    echo -e "    DOMAIN=$DOMAIN bash $APP_DIR/deploy/ssl.sh"
    echo ""
fi
warn "Fill in API keys in $ENV_FILE to activate live SMS/Email/WhatsApp."
