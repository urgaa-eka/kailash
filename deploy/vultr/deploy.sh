#!/usr/bin/env bash
# ==============================================================================
# KAILASH Backend — Vultr VPS Deployment Script
# Run on the Vultr server: bash deploy.sh
# ==============================================================================
set -euo pipefail

APP_DIR="/opt/kailash"
REPO_URL="https://github.com/flywithvvk/kailash.git"
BRANCH="${DEPLOY_BRANCH:-main}"
COMPOSE_FILE="docker-compose.yml"

echo "═══════════════════════════════════════════════════"
echo " Kailash — Vultr Deployment"
echo " Branch: ${BRANCH}"
echo "═══════════════════════════════════════════════════"

install_prerequisites() {
    echo "▶ Checking prerequisites..."
    if ! command -v docker &>/dev/null; then
        echo "  Installing Docker..."
        curl -fsSL https://get.docker.com | sh
        systemctl enable --now docker
        usermod -aG docker "$USER"
    fi
    if ! docker compose version &>/dev/null; then
        echo "  Installing Docker Compose plugin..."
        apt-get update -qq && apt-get install -y -qq docker-compose-plugin
    fi
    if ! command -v nginx &>/dev/null; then
        echo "  Installing Nginx..."
        apt-get update -qq && apt-get install -y -qq nginx certbot python3-certbot-nginx
    fi
    echo "  ✅ Prerequisites ready"
}

update_code() {
    echo "▶ Updating codebase..."
    if [ -d "${APP_DIR}/.git" ]; then
        cd "$APP_DIR"
        git fetch origin "$BRANCH"
        git reset --hard "origin/${BRANCH}"
        git clean -fd
    else
        mkdir -p "$APP_DIR"
        git clone --branch "$BRANCH" "$REPO_URL" "$APP_DIR"
        cd "$APP_DIR"
    fi
    echo "  ✅ Code updated to $(git rev-parse --short HEAD)"
}

check_env() {
    echo "▶ Checking environment..."
    if [ ! -f "${APP_DIR}/backend/.env" ]; then
        echo "  ⚠️  No .env found. Copying example..."
        cp "${APP_DIR}/backend/.env.example" "${APP_DIR}/backend/.env"
        echo "  ❗ EDIT ${APP_DIR}/backend/.env with production values!"
    fi
    echo "  ✅ Environment file present"
}

deploy_containers() {
    echo "▶ Building and deploying containers..."
    cd "$APP_DIR"
    docker compose -f "$COMPOSE_FILE" pull --ignore-buildable 2>/dev/null || true
    docker compose -f "$COMPOSE_FILE" up -d --build --remove-orphans
    echo "  ✅ Containers deployed"
}

setup_nginx() {
    echo "▶ Configuring Nginx reverse proxy..."
    cp "${APP_DIR}/deploy/vultr/nginx-api.conf" /etc/nginx/sites-available/kailash-api
    ln -sf /etc/nginx/sites-available/kailash-api /etc/nginx/sites-enabled/kailash-api
    rm -f /etc/nginx/sites-enabled/default

    if [ ! -f /etc/nginx/proxy_params ]; then
        cat > /etc/nginx/proxy_params <<'EOF'
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_http_version 1.1;
proxy_set_header Connection "";
proxy_connect_timeout 60s;
proxy_send_timeout 60s;
proxy_read_timeout 60s;
EOF
    fi

    nginx -t && systemctl reload nginx
    echo "  ✅ Nginx configured"
}

setup_ssl() {
    echo "▶ Checking SSL certificate..."
    if [ ! -f /etc/letsencrypt/live/api.kailash-ai.in/fullchain.pem ]; then
        mkdir -p /var/www/certbot
        certbot --nginx -d api.kailash-ai.in --non-interactive --agree-tos \
            --email admin@kailash-ai.in --redirect || {
            echo "  ⚠️  Certbot failed. Ensure DNS points api.kailash-ai.in to this server."
        }
    else
        certbot renew --dry-run 2>/dev/null || true
    fi
    echo "  ✅ SSL configured"
}

health_check() {
    echo "▶ Running health check..."
    sleep 10
    local i=0
    while [ $i -lt 6 ]; do
        if curl -sf http://127.0.0.1:8000/api/health > /dev/null 2>&1; then
            echo "  ✅ Backend is healthy!"
            curl -s http://127.0.0.1:8000/api/health | python3 -m json.tool 2>/dev/null || true
            return 0
        fi
        i=$((i + 1))
        echo "  ⏳ Waiting (attempt ${i}/6)..."
        sleep 10
    done
    echo "  ❌ Health check failed. Check: docker compose -f ${COMPOSE_FILE} logs backend"
    return 1
}

setup_cron() {
    echo "▶ Setting up SSL auto-renewal cron..."
    (crontab -l 2>/dev/null | grep -v certbot; echo "0 3 * * * certbot renew --quiet --post-hook 'systemctl reload nginx'") | crontab -
    echo "  ✅ Cron configured"
}

main() {
    install_prerequisites
    update_code
    check_env
    deploy_containers
    setup_nginx
    setup_ssl
    setup_cron
    health_check

    echo ""
    echo "═══════════════════════════════════════════════════"
    echo " ✅ Kailash deployed!"
    echo " API:   https://api.kailash-ai.in"
    echo " Docs:  https://api.kailash-ai.in/api/docs"
    echo "═══════════════════════════════════════════════════"
}

main "$@"
