# NileGov Stack — Hetzner Deployment Guide

## What you need

| Item | Minimum |
|------|---------|
| Hetzner VPS | CX22 (2 vCPU, 4 GB RAM) — Ubuntu 22.04 or 24.04 |
| Domain name | Any domain with DNS pointing to the server IP |
| SSH root access | Required for first setup |

---

## Step 1 — First-time setup

SSH into your Hetzner server as root and run:

```bash
# With a domain (recommended)
DOMAIN=nilegov.mbarara.go.ug \
BRANCH=main \
bash <(curl -fsSL https://raw.githubusercontent.com/sebunya/govproject/main/deploy/setup-hetzner.sh)

# OR clone the repo first then run locally
git clone https://github.com/sebunya/govproject.git /tmp/govproject
DOMAIN=nilegov.mbarara.go.ug bash /tmp/govproject/deploy/setup-hetzner.sh
```

The script will:
- Install Node.js 22, Nginx, Certbot, UFW
- Configure the firewall (SSH + HTTP/HTTPS only)
- Clone the repo to `/opt/nilegov`
- Build client (Vite) and server (TypeScript)
- Seed the demo database
- Create and start the `nilegov` systemd service
- Configure Nginx to serve static files from `client/dist` directly

---

## Step 2 — Enable HTTPS (after DNS is live)

Once your domain resolves to the server IP:

```bash
DOMAIN=nilegov.mbarara.go.ug EMAIL=admin@mbarara.go.ug \
bash /opt/nilegov/deploy/ssl.sh
```

This runs Certbot, installs the production nginx config with TLS, and sets up auto-renewal.

---

## Step 3 — Configure live API keys (optional)

Edit `/opt/nilegov/server/.env`:

```bash
nano /opt/nilegov/server/.env
systemctl restart nilegov
```

Without these keys the system runs in simulation mode — safe for demos.

---

## Day-to-day operations

### Deploy a code update

```bash
BRANCH=main bash /opt/nilegov/deploy/update.sh
```

### Restore demo database state

```bash
bash /opt/nilegov/deploy/reseed.sh
```

### Manual database backup

```bash
bash /opt/nilegov/deploy/backup.sh
```

### Set up daily automated backups

Add to root's crontab (`crontab -e`):

```
0 2 * * * BACKUP_DIR=/var/backups/nilegov bash /opt/nilegov/deploy/backup.sh >> /var/log/nilegov-backup.log 2>&1
```

### View logs

```bash
journalctl -u nilegov -f          # live app logs
tail -f /var/log/nginx/nilegov_access.log   # nginx access log
```

### Check service health

```bash
systemctl status nilegov
curl http://localhost:3001/api/services   # should return JSON
```

---

## File layout on the server

```
/opt/nilegov/
├── client/dist/          ← built React app (served directly by nginx)
├── server/
│   ├── dist/index.js     ← compiled Express API
│   ├── data/
│   │   ├── nilegov.db    ← SQLite database
│   │   └── uploads/      ← uploaded documents
│   └── .env              ← secrets (not committed)
└── deploy/               ← all deployment scripts

/etc/nginx/sites-available/nilegov   ← nginx config
/etc/systemd/system/nilegov.service  ← systemd unit
/var/backups/nilegov/                ← database backups
```

---

## Architecture

```
Browser → Nginx :443
           ├─ /assets/*          → client/dist/assets/  (1-year cache, immutable)
           ├─ /sw.js             → client/dist/sw.js     (no-cache)
           ├─ /api/*             → Node.js :3001         (Express API)
           ├─ /uploads/*         → Node.js :3001         (multer file serving)
           └─ /*                 → client/dist/index.html (SPA fallback)
```

Node.js only handles `/api/` and `/uploads/` — all static assets are served by Nginx directly, which is ~10× faster and uses proper HTTP caching.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Service won't start | `journalctl -u nilegov -n 50 --no-pager` |
| Nginx 502 Bad Gateway | `systemctl status nilegov` — Node may have crashed |
| White screen after deploy | Browser may have cached old SW — open DevTools → Application → Storage → Clear site data |
| Database locked error | Check for stuck `npm run seed` process: `ps aux | grep seed` |
| SSL cert expired | `certbot renew` (should auto-renew via timer) |
