#!/usr/bin/env bash
# ==============================================================================
# KAILASH — Vultr VPS Initial Setup (run ONCE on fresh Ubuntu 22.04/24.04)
# ==============================================================================
set -euo pipefail

echo "═══════════════════════════════════════════════════"
echo " KAILASH — Vultr VPS Initial Setup"
echo "═══════════════════════════════════════════════════"

apt-get update -qq && apt-get upgrade -y -qq

# Firewall
apt-get install -y -qq ufw
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
echo "y" | ufw enable

# Security
apt-get install -y -qq fail2ban
systemctl enable --now fail2ban

# Swap (for low-memory VPS)
if [ ! -f /swapfile ]; then
    fallocate -l 2G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

# Docker
curl -fsSL https://get.docker.com | sh
systemctl enable --now docker

# Nginx + Certbot
apt-get install -y -qq nginx certbot python3-certbot-nginx git curl jq
systemctl enable --now nginx

# App directory
mkdir -p /opt/kailash

# Logrotate
cat > /etc/logrotate.d/kailash <<'EOF'
/var/log/nginx/kailash-api.*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    postrotate
        [ -f /var/run/nginx.pid ] && kill -USR1 $(cat /var/run/nginx.pid)
    endscript
}
EOF

echo ""
echo "═══════════════════════════════════════════════════"
echo " ✅ VPS setup complete!"
echo ""
echo " Next steps:"
echo "   1. Point DNS: api.kailash-ai.in → $(curl -s ifconfig.me)"
echo "   2. cd /opt/kailash && git clone https://github.com/flywithvvk/kailash.git ."
echo "   3. cp backend/.env.example backend/.env"
echo "   4. nano backend/.env  (fill production secrets)"
echo "   5. bash deploy/vultr/deploy.sh"
echo "═══════════════════════════════════════════════════"
