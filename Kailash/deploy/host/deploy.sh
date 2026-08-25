#!/usr/bin/env bash
# ==============================================================================
# KAILASH Backend — Managed-host Deployment Script
# Run on the deployment host (any Docker-capable Linux server): bash deploy.sh
# ==============================================================================
set -euo pipefail

APP_DIR="/opt/kailash"
# The git checkout lives at APP_DIR; the project itself is nested under the
# Kailash/ master folder (see RULES.md), so compose files, scripts.verify and
# the deploy/ configs are resolved from PROJECT_DIR. git operations
# (clone/reset/clean) still run against APP_DIR, the repository root.
PROJECT_DIR="${APP_DIR}/Kailash"
REPO_URL="https://github.com/urgaa-eka/kailash.git"
BRANCH="${DEPLOY_BRANCH:-main}"
COMPOSE_FILE="docker-compose.yml"
COMPOSE_PROFILE="kailash-ai"

# The service set production runs. Decided in
# docs/records/profiled-services-scope.md: the kailash-ai profile's full
# 15-service set, minus `frontend`.
#
# Without --profile this script started four containers -- backend, mongo,
# postgres, redis -- because the other eleven declare profiles: ["kailash-ai"]
# and compose treats a profile-gated service as inert unless the profile is
# enabled. "Deploy the backend" silently meant "deploy the backend and nothing
# it talks to".
#
# `frontend` is named out rather than scaled to zero: it is the nginx SPA
# container for local development, and Firebase Hosting serves the SPA in
# production. Naming services explicitly also keeps `up --build` from building
# frontend/Dockerfile (a full yarn install + CRA build) on the VPS for an image
# that would never run.
#
# Adding a service to docker-compose.yml means adding it here too. Keep in step
# with the same list in .github/workflows/deploy-backend.yml.
PROD_SERVICES=(
    backend mongo postgres redis
    company
    document-ai forecasting anomaly rag vision-gateway
    speech model-registry knowledge-graph automobile-llm
)

echo "═══════════════════════════════════════════════════"
echo " Kailash — Backend Deployment"
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

# Reduce any remote URL form to owner/name. Mirrors normalise_remote() in
# scripts/verify/repo_state.py, which is property-tested across every form git
# accepts -- one that silently returns the URL unchanged would make this guard
# reject every valid checkout, turning a safety feature into an outage.
normalise_remote() {
    local url="$1"
    url="${url%/}"
    url="${url%.git}"
    case "$url" in
        *://*)                       # scheme://[user@]host/owner/name
            url="${url#*://}"
            url="${url#*@}"
            url="${url#*/}"
            ;;
        *@*:*)                       # scp-like: user@host:owner/name
            url="${url#*:}"
            ;;
        *:*)                         # host:owner/name
            url="${url#*:}"
            ;;
    esac
    printf '%s' "$url"
}

# Called before every destructive git operation below.
#
# `git reset --hard`, `git clean -fd` and `git clone` all destroy whatever is
# in the target directory. If APP_DIR is not the checkout we think it is --
# wrong repository, or not a work tree at all -- those commands do their work
# anyway, against the wrong thing.
#
# Not hypothetical: REPO_URL in this script named a different owner than
# `git remote get-url origin` reported, for as long as this script existed.
# The wrong slug is deliberately not written out here -- this file is the one
# place a stray repository reference is most dangerous, and config_drift
# treats every slug in it as authoritative.
assert_expected_checkout() {
    local dir="$1"
    local expected="urgaa-eka/kailash"

    if [ ! -d "${dir}/.git" ]; then
        echo "  ✖ ${dir} is not a git work tree; refusing to run a destructive git operation there" >&2
        return 1
    fi

    local origin
    origin="$(git -C "$dir" remote get-url origin 2>/dev/null || true)"
    if [ -z "$origin" ]; then
        echo "  ✖ ${dir} has no origin remote; refusing" >&2
        return 1
    fi

    local slug
    slug="$(normalise_remote "$origin")"
    if [ "$slug" != "$expected" ]; then
        echo "  ✖ ${dir} origin is '${slug}', expected '${expected}'" >&2
        echo "    Refusing: git reset --hard and git clean -fd would destroy a checkout of another repository." >&2
        return 1
    fi

    echo "  ✅ ${dir} is a checkout of ${expected}"
}

update_code() {
    echo "▶ Updating codebase..."
    if [ -d "${APP_DIR}/.git" ]; then
        assert_expected_checkout "$APP_DIR"
        cd "$APP_DIR"
        git fetch origin "$BRANCH"
        git reset --hard "origin/${BRANCH}"
        git clean -fd
    else
        # A clone into a non-empty directory is equally destructive in effect:
        # it either fails or leaves a half-populated tree. Refuse unless the
        # directory is absent or empty.
        if [ -e "$APP_DIR" ] && [ -n "$(ls -A "$APP_DIR" 2>/dev/null)" ]; then
            echo "  ✖ ${APP_DIR} exists, is not empty, and is not a git work tree; refusing to clone over it" >&2
            return 1
        fi
        mkdir -p "$APP_DIR"
        git clone --branch "$BRANCH" "$REPO_URL" "$APP_DIR"
        cd "$APP_DIR"
        assert_expected_checkout "$APP_DIR"
    fi

    # After `git reset --hard`, a clean tree is the definition of "deployed
    # what was committed". Any modification reported here means somebody
    # edited files on the production server; deploying would silently bake
    # those edits into the running containers, so the deploy terminates and
    # prints each modified path instead (Requirement 9.2).
    if command -v python3 >/dev/null 2>&1; then
        if ! (cd "$PROJECT_DIR" && python3 -m scripts.verify.repo_state); then
            echo "  ✖ Working tree on the server does not match the committed state; refusing to deploy." >&2
            return 1
        fi
    else
        echo "  ⚠️  python3 not found; repo-state verification skipped on this host" >&2
    fi

    echo "  ✅ Code updated to $(git rev-parse --short HEAD)"
}

check_env() {
    echo "▶ Checking environment..."
    if [ ! -f "${PROJECT_DIR}/backend/.env" ]; then
        echo "  ⚠️  No .env found. Copying example..."
        cp "${PROJECT_DIR}/backend/.env.example" "${PROJECT_DIR}/backend/.env"
        echo "  ❗ EDIT ${PROJECT_DIR}/backend/.env with production values!"
    fi
    echo "  ✅ Environment file present"
}

deploy_containers() {
    echo "▶ Building and deploying ${#PROD_SERVICES[@]} containers..."
    cd "$PROJECT_DIR"
    # The commit actually checked out, exported so compose substitutes it into
    # the backend environment (docker-compose.yml: GIT_COMMIT=${GIT_COMMIT:-unknown})
    # and /api/health reports what is running (Requirement 6.6). Read from the
    # work tree rather than passed in, so it is the deployed code by
    # construction. Keep in step with the same export in
    # .github/workflows/deploy-backend.yml.
    GIT_COMMIT="$(git rev-parse HEAD)"
    export GIT_COMMIT
    docker compose -f "$COMPOSE_FILE" --profile "$COMPOSE_PROFILE" \
        pull --ignore-buildable "${PROD_SERVICES[@]}" 2>/dev/null || true
    docker compose -f "$COMPOSE_FILE" --profile "$COMPOSE_PROFILE" \
        up -d --build --remove-orphans "${PROD_SERVICES[@]}"
    docker compose -f "$COMPOSE_FILE" --profile "$COMPOSE_PROFILE" ps
    echo "  ✅ Containers deployed"
}

# How many commit-tagged backend images to keep, counting the one just
# written. A conservative default: task 10.4 wants this set from the disk
# headroom the task 4.5 record quantifies, and that record does not exist yet
# (the design proposed 10 as a starting point). Keep in step with the same
# value in .github/workflows/deploy-backend.yml and docs/runbooks/rollback.md.
RETAINED_IMAGE_TAGS=3

tag_backend_image() {
    echo "▶ Tagging backend image by deployed commit..."
    local sha
    sha="${GIT_COMMIT:-$(git -C "$APP_DIR" rev-parse HEAD)}"

    # Resolve the image the backend container actually runs rather than
    # guessing the compose-derived name: compose names built images after the
    # project directory, so the name differs between /opt/kailash and a
    # developer checkout while `.Image` never does.
    local image_id
    image_id="$(docker inspect kailash-backend --format '{{.Image}}')"
    docker tag "$image_id" "kailash-backend:${sha}"

    # Task 10.4: the tag must verifiably exist on the host after a deploy.
    docker image inspect "kailash-backend:${sha}" > /dev/null
    echo "  ✅ Tagged kailash-backend:${sha}"

    # Prune commit tags beyond the retention depth. `docker image ls` lists
    # newest first; only full 40-hex tags are candidates, so :latest and any
    # hand-made tag are left alone, as is the tag just written.
    local pruned=0 tag
    while read -r tag; do
        [ -n "$tag" ] || continue
        if docker rmi "kailash-backend:${tag}" > /dev/null 2>&1; then
            pruned=$((pruned + 1))
        else
            echo "  ⚠️  Could not remove kailash-backend:${tag} (in use?)"
        fi
    done < <(docker image ls kailash-backend --format '{{.Tag}}' \
        | grep -E '^[0-9a-f]{40}$' | grep -vx "$sha" \
        | tail -n +"$RETAINED_IMAGE_TAGS")
    [ "$pruned" -eq 0 ] || echo "  ✅ Pruned ${pruned} old commit tag(s)"
}

setup_nginx() {
    echo "▶ Configuring Nginx reverse proxy..."
    # The full configs reference /etc/letsencrypt/live/<host>/ certificates,
    # so each is installed only once its certificate exists -- otherwise
    # `nginx -t` fails on the config this script itself installed, which on a
    # fresh box killed the deploy before setup_ssl ever ran. setup_ssl issues
    # certificates with `certonly` (no config edits) and re-runs this.
    if [ -f /etc/letsencrypt/live/api.kailash-ai.in/fullchain.pem ]; then
        cp "${PROJECT_DIR}/deploy/host/nginx-api.conf" /etc/nginx/sites-available/kailash-api
        ln -sf /etc/nginx/sites-available/kailash-api /etc/nginx/sites-enabled/kailash-api
    else
        echo "  ⏭  api certificate absent; config deferred until setup_ssl issues it"
    fi
    if [ -f /etc/letsencrypt/live/staging-api.kailash-ai.in/fullchain.pem ] \
        && [ -f "${PROJECT_DIR}/deploy/staging/nginx-staging-api.conf" ]; then
        cp "${PROJECT_DIR}/deploy/staging/nginx-staging-api.conf" \
            /etc/nginx/sites-available/kailash-staging-api
        ln -sf /etc/nginx/sites-available/kailash-staging-api \
            /etc/nginx/sites-enabled/kailash-staging-api
    fi
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
    echo "▶ Checking SSL certificates..."
    local issued_new=0
    local host
    for host in api.kailash-ai.in staging-api.kailash-ai.in; do
        if [ ! -f "/etc/letsencrypt/live/${host}/fullchain.pem" ]; then
            mkdir -p /var/www/certbot
            # certonly: issue without touching any nginx config, so this works
            # on a box that has no server block for the hostname yet.
            certbot certonly --nginx -d "$host" --non-interactive --agree-tos \
                --email admin@kailash-ai.in && issued_new=1 || {
                echo "  ⚠️  Certbot failed for ${host}. Ensure DNS points it at this server."
            }
        fi
    done
    if [ "$issued_new" -eq 1 ]; then
        # Now that certificates exist, the deferred configs can be installed.
        setup_nginx
    fi
    certbot renew --dry-run 2>/dev/null || true
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
    # `|| true` twice: on a fresh box `crontab -l` exits 1 (no crontab yet)
    # and `grep -v` exits 1 on empty input -- under `pipefail` either one
    # killed the whole deploy at its very last step.
    { crontab -l 2>/dev/null || true; } | { grep -v certbot || true; } \
        | { cat; echo "0 3 * * * certbot renew --quiet --post-hook 'systemctl reload nginx'"; } \
        | crontab -
    echo "  ✅ Cron configured"
}

main() {
    install_prerequisites
    update_code
    check_env
    deploy_containers
    tag_backend_image
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
