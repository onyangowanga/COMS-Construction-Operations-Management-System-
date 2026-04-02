#!/bin/bash

set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/root/coms}"
COMPOSE_FILE="docker-compose.prod.yml"
declare -a COMPOSE_BIN=()

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

resolve_compose() {
    if docker compose version >/dev/null 2>&1; then
        COMPOSE_BIN=(docker compose)
    elif command -v docker-compose >/dev/null 2>&1; then
        COMPOSE_BIN=(docker-compose)
    else
        print_error "Docker Compose is not installed on the VPS."
        exit 1
    fi
}

compose() {
    "${COMPOSE_BIN[@]}" --env-file .env.production -f "$COMPOSE_FILE" "$@"
}

show_diagnostics() {
    if [ "${#COMPOSE_BIN[@]}" -eq 0 ]; then
        return 0
    fi

    print_warning "Container status at failure time:"
    compose ps || true

    print_warning "Last 80 lines from web container:"
    compose logs --tail=80 web || true

    print_warning "Last 80 lines from db container:"
    compose logs --tail=80 db || true
}

on_error() {
    local line_no="$1"
    local failed_command="$2"

    print_error "Deployment step failed on line ${line_no}: ${failed_command}"
    show_diagnostics
}

trap 'on_error ${LINENO} "$BASH_COMMAND"' ERR

escape_env_dollars() {
    local value="$1"

    # Preserve already escaped dollars, then escape any remaining single dollar.
    value="${value//\$\$/__COMS_ESC_DOLLAR__}"
    value="${value//\$/\$\$}"
    value="${value//__COMS_ESC_DOLLAR__/\$\$}"

    printf '%s' "$value"
}

sanitize_env_file_for_compose() {
    local env_file="$PROJECT_DIR/.env.production"
    local temp_file
    local changed=0

    [ -f "$env_file" ] || return 0

    temp_file="$(mktemp)"

    while IFS= read -r line || [ -n "$line" ]; do
        if [[ -z "$line" || "$line" =~ ^[[:space:]]*# || "$line" != *=* ]]; then
            printf '%s\n' "$line" >> "$temp_file"
            continue
        fi

        local key="${line%%=*}"
        local value="${line#*=}"
        local escaped_value

        escaped_value="$(escape_env_dollars "$value")"
        if [ "$escaped_value" != "$value" ]; then
            changed=1
        fi

        printf '%s=%s\n' "$key" "$escaped_value" >> "$temp_file"
    done < "$env_file"

    if [ "$changed" -eq 1 ]; then
        cp "$env_file" "$env_file.before-compose-escape-$(date +%Y%m%d_%H%M%S)"
        mv "$temp_file" "$env_file"
        print_warning "Detected unescaped '$' in .env.production and auto-escaped it for Docker Compose compatibility."
    else
        rm -f "$temp_file"
    fi
}

normalize_line_endings() {
    find "$PROJECT_DIR" -type f \( -name "*.sh" -o -name ".env*" \) -exec sed -i 's/\r$//' {} + 2>/dev/null || true
}

wait_for_database() {
    print_status "Waiting for database to become ready..."

    for attempt in $(seq 1 30); do
        if compose exec -T db sh -lc 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"' >/dev/null 2>&1; then
            print_status "Database is ready."
            return 0
        fi

        sleep 2
    done

    print_error "Database never became ready."
    return 1
}

run_health_check() {
    print_status "Checking application health..."
    sleep 5

    if command -v curl >/dev/null 2>&1; then
        status_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/health/ || true)
    elif command -v wget >/dev/null 2>&1; then
        wget -q --spider http://localhost/health/ && status_code="200" || status_code="000"
    else
        print_warning "curl and wget are both unavailable; skipping HTTP health check."
        return 0
    fi

    if [ "$status_code" != "200" ]; then
        print_error "Health check failed with status $status_code"
        return 1
    fi

    print_status "Application health check passed."
}

echo "================================"
echo "COMS Deployment Script"
echo "================================"
echo ""

if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root"
    exit 1
fi

cd "$PROJECT_DIR"

if [ ! -f "$COMPOSE_FILE" ]; then
    print_error "${PROJECT_DIR}/${COMPOSE_FILE} not found"
    exit 1
fi

resolve_compose
normalize_line_endings

if [ ! -f .env.production ]; then
    print_warning ".env.production not found. Compose will likely fail because docker-compose.prod.yml expects it."
fi

sanitize_env_file_for_compose

print_status "Stopping existing containers..."
compose down --remove-orphans || true

print_status "Building Docker images..."
compose build --pull web frontend nginx

print_status "Starting containers..."
compose up -d

wait_for_database

print_status "Running database migrations..."
if ! compose exec -T web python manage.py migrate --noinput; then
    print_error "Database migration failed."
    print_warning "Django migration state:"
    compose exec -T web python manage.py showmigrations --plan || true
    print_warning "Recent web logs after migration failure:"
    compose logs --tail=120 web || true
    exit 1
fi

print_status "Collecting static files..."
if ! compose exec -T web python manage.py collectstatic --noinput; then
    print_error "collectstatic failed."
    print_warning "Recent web logs after collectstatic failure:"
    compose logs --tail=120 web || true
    exit 1
fi

print_status "Current container status:"
compose ps

run_health_check

echo "================================"
echo "Deployment completed successfully!"
echo "================================"