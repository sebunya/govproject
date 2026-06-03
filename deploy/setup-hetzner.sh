#!/usr/bin/env bash
# NileGov Stack — Hetzner VPS first-time setup
# Run as root on a fresh Ubuntu 22.04 / 24.04 node.
# Usage: bash setup-hetzner.sh

set -euo pipefail

APP_USER="nilegov"
APP_DIR="/opt/nilegov"
NODE_VERSION="22"
REPO_URL="${REPO_URL:-https://github.com/sebunya/govproject.git}"
BRANCH="${BRANCH:-main}"
DOMAIN="${DOMAIN:-}"   # set this to your domain/IP for nginx

echo "==> Installing system packages"
apt-get update -qq
apt-get install -y -qq curl git nginx

echo "==> Installing Node.js $NODE_VERSION"
curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash -
apt-get install -y -qq nodejs
node -v && npm -v

echo "==> Creating app user"
id "$APP_USER" &>/dev/null || useradd -m -s /bin/bash "$APP_USER"

echo "==> Cloning repository"
rm -rf "$APP_DIR"
git clone --branch "$BRANCH" --depth 1 "$REPO_URL" "$APP_DIR"
chown -R "$APP_USER":"$APP_USER" "$APP_DIR"

echo "==> Installing dependencies and building"
cd "$APP_DIR"
sudo -u "$APP_USER" npm install --workspaces
sudo -u "$APP_USER" npm run build        # builds Vite + compiles TypeScript

echo "==> Seeding database (camera-ready demo state)"
sudo -u "$APP_USER" npm run seed

echo "==> Writing systemd service"
cat > /etc/systemd/system/nilegov.service <<EOF
[Unit]
Description=NileGov Stack
After=network.target

[Service]
User=$APP_USER
WorkingDirectory=$APP_DIR
Environment=NODE_ENV=production
Environment=PORT=3001
ExecStart=/usr/bin/node --experimental-sqlite $APP_DIR/server/dist/index.js
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable nilegov
systemctl restart nilegov
echo "==> Service started: $(systemctl is-active nilegov)"

echo "==> Writing nginx config"
NGINX_CONF="/etc/nginx/sites-available/nilegov"
cat > "$NGINX_CONF" <<NGINX
server {
    listen 80;
    server_name ${DOMAIN:-_};

    client_max_body_size 10M;

    location / {
        proxy_pass         http://127.0.0.1:3001;
        proxy_http_version 1.1;
        proxy_set_header   Host \$host;
        proxy_set_header   X-Real-IP \$remote_addr;
        proxy_set_header   X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_read_timeout 60s;
    }
}
NGINX

ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/nilegov
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

echo ""
echo "======================================================"
echo "  NileGov Stack is running on http://${DOMAIN:-<server-ip>}"
echo "======================================================"
echo ""
echo "  Citizen portal : /portal"
echo "  Officer desk   : /desk"
echo "  Supervisor     : /supervisor"
echo "  Leadership     : /dashboard"
echo ""
echo "  Logs: journalctl -u nilegov -f"
echo "  Re-seed: sudo -u $APP_USER bash -c 'cd $APP_DIR && npm run seed'"
