#!/usr/bin/env bash
# ==============================================================================
# Rotate the datastore credentials on a stack that is already running.
#
# The trap this exists to avoid:
#
#   POSTGRES_PASSWORD and the Redis requirepass are only read when the volume
#   is FIRST initialised. Editing .env and restarting does not change the
#   password the database actually accepts -- it changes the one the clients
#   present. The stack then comes up unable to authenticate against its own
#   datastores, and the symptom (connection refused / auth failed) points at
#   the application rather than at the rotation.
#
#   So the password must be changed INSIDE the running database first, and
#   only then in .env.
#
# Usage:  bash deploy/vultr/rotate-credentials.sh [target-dir]
# ==============================================================================
set -euo pipefail

TARGET_DIR="${1:-/opt/kailash}"
ENV_FILE="${TARGET_DIR}/.env"
COMPOSE_FILE="${TARGET_DIR}/docker-compose.yml"

[ -f "$ENV_FILE" ] || { echo "✖ ${ENV_FILE} not found. Run bootstrap-env.sh first." >&2; exit 1; }
[ -f "$COMPOSE_FILE" ] || { echo "✖ ${COMPOSE_FILE} not found." >&2; exit 1; }

cd "$TARGET_DIR"

generate() {
    if command -v openssl &>/dev/null; then
        openssl rand -base64 32 | tr -d '\n=' | tr '+/' '-_'
    else
        head -c 32 /dev/urandom | base64 | tr -d '\n=' | tr '+/' '-_'
    fi
}

read_env() { grep -E "^${1}=" "$ENV_FILE" | head -1 | cut -d= -f2-; }

set_env() {
    local key="$1" value="$2"
    if grep -qE "^${key}=" "$ENV_FILE"; then
        sed -i "s|^${key}=.*|${key}=${value}|" "$ENV_FILE"
    else
        echo "${key}=${value}" >> "$ENV_FILE"
    fi
}

backup="${ENV_FILE}.$(date -u +%Y%m%dT%H%M%SZ).bak"
cp -p "$ENV_FILE" "$backup"
echo "▶ Backed up ${ENV_FILE} -> ${backup}"

# ---- Postgres -------------------------------------------------------------
NEW_PG="$(generate)"
echo "▶ Rotating POSTGRES_PASSWORD inside the running database..."
if docker compose ps --status running postgres >/dev/null 2>&1; then
    docker compose exec -T postgres \
        psql -U kailash -d kailash -v ON_ERROR_STOP=1 \
        -c "ALTER USER kailash WITH PASSWORD '${NEW_PG}';"
    set_env POSTGRES_PASSWORD "$NEW_PG"
    echo "  ✅ Postgres password changed in the database and in .env"
else
    echo "  ⚠️  postgres is not running; rotating .env only." >&2
    echo "     If its volume already exists this WILL break authentication." >&2
    set_env POSTGRES_PASSWORD "$NEW_PG"
fi

# ---- Redis ----------------------------------------------------------------
NEW_REDIS="$(generate)"
OLD_REDIS="$(read_env REDIS_PASSWORD)"
echo "▶ Rotating REDIS_PASSWORD..."
if docker compose ps --status running redis >/dev/null 2>&1; then
    # CONFIG SET takes effect immediately; the compose command line supplies it
    # again on the next restart, so both paths must agree.
    docker compose exec -T redis \
        redis-cli -a "$OLD_REDIS" --no-auth-warning CONFIG SET requirepass "$NEW_REDIS" >/dev/null
    set_env REDIS_PASSWORD "$NEW_REDIS"
    echo "  ✅ Redis requirepass changed in the running server and in .env"
else
    echo "  ⚠️  redis is not running; rotating .env only." >&2
    set_env REDIS_PASSWORD "$NEW_REDIS"
fi

# ---- Application secrets --------------------------------------------------
# These are read at startup and stored nowhere, so .env is the only place.
for key in PLATFORM_INTERNAL_TOKEN SECRET_KEY; do
    set_env "$key" "$(generate)"
    echo "▶ Rotated ${key}"
done

echo ""
echo "▶ Restarting so every client picks up the new values..."
docker compose -f docker-compose.yml up -d --no-build

echo ""
echo "✅ Rotation complete. Verify:"
echo "    docker compose ps"
echo "    curl -sf http://127.0.0.1:8000/api/health"
echo ""
echo "Rotating SECRET_KEY invalidates every issued JWT. Users must sign in again."
echo "That is the point: tokens signed with the old key can no longer be forged."
echo ""
echo "Previous values are in ${backup} (0600). Delete it once the stack is healthy."
