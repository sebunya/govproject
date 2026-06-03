#!/usr/bin/env bash

# NileGov VPS Initial Host Provisioning and Hardening Script
# Designed for Ubuntu LTS. Must be executed as root.

set -euo pipefail

# --- Configuration Constants ---
SWAP_SIZE_GB=2
DEPLOY_USER="nilegov"
SSH_CONFIG_FILE="/etc/ssh/sshd_config"
DOCKER_DAEMON_FILE="/etc/docker/daemon.json"

# Log functions
log_info() { echo -e "\e[32m[INFO]\e[0m $*"; }
log_warn() { echo -e "\e[33m[WARN]\e[0m $*"; }
log_error() { echo -e "\e[31m[ERROR]\e[0m $*" >&2; }

# Check root privileges
if [ "$(id -u)" -ne 0 ]; then
    log_error "This script must be executed as root. Use sudo -i or run as root user."
    exit 1
fi

log_info "Starting host provisioning for NileGov Stack..."

# 1. Update OS and Install Base Tools
log_info "Updating system packages..."
apt-get update && apt-get upgrade -y
apt-get install -y curl wget git ufw gnupg2 ca-certificates lsb-release software-properties-common fail2ban

# 2. Setup Swap File (Resource-consciousness for low RAM)
if swapon --show | grep -q "/swapfile"; then
    log_warn "Swap file already exists. Skipping swap creation."
else
    log_info "Creating ${SWAP_SIZE_GB}GB Swap File..."
    fallocate -l "${SWAP_SIZE_GB}G" /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=$((SWAP_SIZE_GB * 1024))
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    log_info "Swap file successfully created and mounted."
fi

# 3. Kernel Tuning for Single-Node Redis/DB stability
log_info "Tuning kernel params in /etc/sysctl.conf..."
# Enable memory overcommit so Redis saves snapshots reliably without OOM
if ! grep -q "vm.overcommit_memory" /etc/sysctl.conf; then
    echo "vm.overcommit_memory = 1" >> /etc/sysctl.conf
    sysctl -w vm.overcommit_memory=1
fi
# Adjust swappiness so VPS prefers physical RAM over Swap
if ! grep -q "vm.swappiness" /etc/sysctl.conf; then
    echo "vm.swappiness = 10" >> /etc/sysctl.conf
    sysctl -w vm.swappiness=10
fi

# 4. Create Non-Root Deployment User
if id "$DEPLOY_USER" &>/dev/null; then
    log_warn "User '${DEPLOY_USER}' already exists. Skipping creation."
else
    log_info "Creating non-root deployment user: '${DEPLOY_USER}'..."
    useradd -m -s /bin/bash "$DEPLOY_USER"
    usermod -aG sudo "$DEPLOY_USER"
    
    # Configure Passwordless Sudo for deployment operations
    echo "$DEPLOY_USER ALL=(ALL) NOPASSWD:ALL" > "/etc/sudoers.d/$DEPLOY_USER"
    chmod 0440 "/etc/sudoers.d/$DEPLOY_USER"

    # Propagate Authorized SSH Keys from Root
    if [ -f /root/.ssh/authorized_keys ]; then
        mkdir -p "/home/$DEPLOY_USER/.ssh"
        cp /root/.ssh/authorized_keys "/home/$DEPLOY_USER/.ssh/authorized_keys"
        chown -R "$DEPLOY_USER:$DEPLOY_USER" "/home/$DEPLOY_USER/.ssh"
        chmod 700 "/home/$DEPLOY_USER/.ssh"
        chmod 600 "/home/$DEPLOY_USER/.ssh/authorized_keys"
        log_info "Authorized SSH keys copied to '${DEPLOY_USER}'."
    else
        log_warn "No SSH authorized_keys found in root. Be sure to configure SSH keys for '${DEPLOY_USER}' manually."
    fi
fi

# Parse command-line arguments
SKIP_SSH=false
for arg in "$@"; do
    if [ "$arg" = "--skip-ssh" ]; then
        SKIP_SSH=true
    fi
done

# 5. SSH Hardening (Restricted SSH)
if [ "$SKIP_SSH" = "true" ]; then
    log_warn "Skipping SSH hardening as requested via --skip-ssh flag."
else
    log_info "Running preflight SSH verification..."
    KEYS_FILE="/home/${DEPLOY_USER}/.ssh/authorized_keys"
    
    # Verify that the authorized_keys file exists and has content
    if [ ! -f "$KEYS_FILE" ] || [ ! -s "$KEYS_FILE" ]; then
        log_warn "CRITICAL WARNING: No SSH authorized keys found for user '${DEPLOY_USER}' at ${KEYS_FILE}."
        log_warn "Disabling password/root login now will lock you out of this server!"
    fi

    # Interactive confirmation prompt
    PROCEED_SSH="n"
    if [ -t 0 ]; then
        read -p "Do you want to proceed with hardening SSH (disables password authentication and root login)? [y/N]: " -n 1 -r
        echo
        PROCEED_SSH=$REPLY
    else
        log_warn "Non-interactive environment detected. Skipping SSH hardening by default to prevent lockout."
        PROCEED_SSH="n"
    fi

    if [[ "$PROCEED_SSH" =~ ^[Yy]$ ]]; then
        log_info "Hardening SSH configuration..."
        if [ -f "$SSH_CONFIG_FILE" ]; then
            # Disable Password Authentication (Enforce Keys only)
            sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/g' "$SSH_CONFIG_FILE"
            # Disable Root Password/Key login (Log in as deploy user first, then sudo)
            sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/g' "$SSH_CONFIG_FILE"
            # Enable Pubkey Authentication
            sed -i 's/^#\?PubkeyAuthentication.*/PubkeyAuthentication yes/g' "$SSH_CONFIG_FILE"
            
            # Restart SSH Daemon to apply settings
            systemctl restart sshd
            log_info "SSH hardened. Password auth disabled, root login disabled."
        else
            log_error "SSH configuration file not found at ${SSH_CONFIG_FILE}."
        fi
    else
        log_info "SSH hardening skipped. Password and root authentication remain enabled."
    fi
fi

# 6. Firewall Hardening via UFW
log_info "Configuring UFW firewall rules..."
ufw default deny incoming
ufw default allow outgoing
ufw allow OpenSSH
ufw allow http
ufw allow https
# Enable firewall (non-interactive mode)
ufw --force enable
log_info "Firewall activated. Incoming traffic restricted to SSH, HTTP, and HTTPS."

# 7. Install Docker and Docker Compose
log_info "Installing Docker Engine and Compose plugin..."
# Add Docker's official GPG key
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor --yes -o /etc/apt/keyrings/docker.gpg

# Set up the repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list

apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Grant deploy user docker group membership
usermod -aG docker "$DEPLOY_USER"

# 8. Configure Docker Log Rotation (Prevent disk-space leaks)
log_info "Setting up Docker daemon log rotation..."
mkdir -p /etc/docker
cat <<EOF > "$DOCKER_DAEMON_FILE"
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF
systemctl restart docker
log_info "Docker log rotation configured (max 10MB per container, keeping 3 files)."

# 9. Install Host Nginx and Certbot for SSL
log_info "Installing Nginx and Certbot for SSL..."
apt-get install -y nginx certbot python3-certbot-nginx

# Disable Nginx default site configuration to avoid conflicts
if [ -f /etc/nginx/sites-enabled/default ]; then
    rm /etc/nginx/sites-enabled/default
    systemctl restart nginx
fi

log_info "========================================================="
log_info " NileGov Stack Host Provisioning Completed Successfully!  "
log_info "========================================================="
log_info "Security Reminders:"
log_info "1. Log in now using SSH keys as the '${DEPLOY_USER}' user: ssh ${DEPLOY_USER}@<host_ip>"
log_info "2. Docker and Docker Compose are configured."
log_info "3. Set up your reverse proxy by placing the site config in /etc/nginx/sites-available/"
log_info "4. Set up SSL certificates by running: sudo certbot --nginx -d yourdomain.com"
log_info "========================================================="
