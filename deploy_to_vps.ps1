param(
    [string]$VpsHost = "156.232.88.156",
    [string]$VpsUser = "root",
    [string]$VpsProjectDir = "/root/coms",
    [string]$RemoteEnvFile = ".env.production",
    [switch]$NoBackup,
    [switch]$SkipHealthCheck
)

$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot
$ArchiveName = "coms-deploy-{0}.tar.gz" -f (Get-Date -Format "yyyyMMdd_HHmmss")
$RemoteArchivePath = "/tmp/$ArchiveName"
$TempRoot = Join-Path $env:TEMP ("coms-deploy-{0}" -f (Get-Date -Format "yyyyMMdd_HHmmss"))
$ArchivePath = Join-Path $TempRoot $ArchiveName

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] " -ForegroundColor Green -NoNewline
    Write-Host $Message
}

function Write-Step {
    param([string]$Message)
    Write-Host "[STEP] " -ForegroundColor Cyan -NoNewline
    Write-Host $Message
}

function Write-Warn {
    param([string]$Message)
    Write-Host "[WARN] " -ForegroundColor Yellow -NoNewline
    Write-Host $Message
}

function Fail {
    param([string]$Message)
    Write-Host "[ERROR] " -ForegroundColor Red -NoNewline
    Write-Host $Message
    exit 1
}

function Require-Command {
    param([string]$CommandName)

    if (-not (Get-Command $CommandName -ErrorAction SilentlyContinue)) {
        Fail "$CommandName is required but was not found on this machine."
    }
}

function Invoke-NativeCommand {
    param(
        [string]$FilePath,
        [string[]]$Arguments
    )

    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        Fail "Command failed: $FilePath $($Arguments -join ' ')"
    }
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "COMS Local-to-VPS Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path (Join-Path $ProjectRoot "manage.py"))) {
    Fail "manage.py not found. Run this script from the COMS project folder."
}

if (-not (Test-Path (Join-Path $ProjectRoot "docker-compose.prod.yml"))) {
    Fail "docker-compose.prod.yml not found in the COMS project folder."
}

Require-Command "ssh"
Require-Command "scp"
Require-Command "tar.exe"

Write-Info "Source: $ProjectRoot"
Write-Info "Target: ${VpsUser}@${VpsHost}:${VpsProjectDir}"

Write-Step "Validating SSH access to the VPS..."
Invoke-NativeCommand -FilePath "ssh" -Arguments @(
    "-o", "BatchMode=yes",
    "-o", "ConnectTimeout=10",
    "-o", "StrictHostKeyChecking=no",
    "${VpsUser}@${VpsHost}",
    "echo connected"
)

if (Test-Path $TempRoot) {
    Remove-Item -Path $TempRoot -Recurse -Force
}

New-Item -ItemType Directory -Path $TempRoot | Out-Null

$excludeArgs = @(
    "--exclude=.git",
    "--exclude=.github",
    "--exclude=.venv",
    "--exclude=venv",
    "--exclude=__pycache__",
    "--exclude=*.pyc",
    "--exclude=*.pyo",
    "--exclude=*.log",
    "--exclude=*.tar.gz",
    "--exclude=*.zip",
    "--exclude=node_modules",
    "--exclude=.next",
    "--exclude=./postgres_data",
    "--exclude=./redis_data",
    "--exclude=.env",
    "--exclude=.env.local",
    "--exclude=.env.production",
    "--exclude=.vscode",
    "--exclude=.idea"
)

Write-Step "Creating a clean deployment archive from the local project..."
$tarArgs = @("-czf", $ArchivePath) + $excludeArgs + @("-C", $ProjectRoot, ".")
Invoke-NativeCommand -FilePath "tar.exe" -Arguments $tarArgs

$archiveList = (& tar.exe -tf $ArchivePath)
if ($LASTEXITCODE -ne 0) {
    Fail "Failed to inspect deployment archive contents."
}

if (-not ($archiveList | Select-String -SimpleMatch "./apps/media/__init__.py")) {
    Fail "Archive validation failed: ./apps/media/__init__.py is missing. Deployment aborted to prevent broken VPS rollout."
}

$archiveSizeMb = [math]::Round((Get-Item $ArchivePath).Length / 1MB, 2)
Write-Info "Archive created: $ArchiveName ($archiveSizeMb MB)"

Write-Step "Uploading the archive to the VPS..."
Invoke-NativeCommand -FilePath "scp" -Arguments @(
    "-o", "ConnectTimeout=20",
    "-o", "StrictHostKeyChecking=no",
    $ArchivePath,
    "${VpsUser}@${VpsHost}:${RemoteArchivePath}"
)

$remoteScript = @'
set -euo pipefail

ARCHIVE_PATH="$1"
PROJECT_DIR="$2"
REMOTE_ENV_FILE="$3"
NO_BACKUP="$4"
SKIP_HEALTH_CHECK="$5"
BACKUP_ROOT="/root/coms-backups"
PRESERVE_ROOT="$(mktemp -d)"

print_info() {
    printf '[VPS] %s\n' "$1"
}

print_error() {
    printf '[VPS ERROR] %s\n' "$1" >&2
}

resolve_compose() {
    if docker compose version >/dev/null 2>&1; then
        COMPOSE_BIN=(docker compose)
    elif command -v docker-compose >/dev/null 2>&1; then
        COMPOSE_BIN=(docker-compose)
    else
        print_error 'Docker Compose is not installed on the VPS.'
        exit 1
    fi
}

compose() {
    "${COMPOSE_BIN[@]}" -f docker-compose.prod.yml "$@"
}

cleanup() {
    rm -rf "$PRESERVE_ROOT"
}
trap cleanup EXIT

mkdir -p "$PROJECT_DIR"

if [ ! -f "$ARCHIVE_PATH" ]; then
    print_error "Archive not found: $ARCHIVE_PATH"
    exit 1
fi

print_info 'Detecting Docker Compose...'
resolve_compose

if [ -f "$PROJECT_DIR/docker-compose.prod.yml" ]; then
    print_info 'Stopping existing containers...'
    (cd "$PROJECT_DIR" && compose down --remove-orphans) || true
fi

if [ "$NO_BACKUP" != "true" ] && [ -f "$PROJECT_DIR/docker-compose.prod.yml" ]; then
    timestamp="$(date +%Y%m%d_%H%M%S)"
    backup_dir="$BACKUP_ROOT/deployment-$timestamp"
    mkdir -p "$backup_dir"

    if [ -f "$PROJECT_DIR/$REMOTE_ENV_FILE" ]; then
        cp "$PROJECT_DIR/$REMOTE_ENV_FILE" "$backup_dir/$REMOTE_ENV_FILE"
    fi

    if [ -d "$PROJECT_DIR/nginx/ssl" ]; then
        mkdir -p "$backup_dir/nginx"
        cp -a "$PROJECT_DIR/nginx/ssl" "$backup_dir/nginx/ssl"
    fi

    print_info "Backup created at $backup_dir"
fi

if [ -f "$PROJECT_DIR/$REMOTE_ENV_FILE" ]; then
    cp "$PROJECT_DIR/$REMOTE_ENV_FILE" "$PRESERVE_ROOT/$REMOTE_ENV_FILE"
fi

if [ -d "$PROJECT_DIR/nginx/ssl" ]; then
    mkdir -p "$PRESERVE_ROOT/nginx"
    cp -a "$PROJECT_DIR/nginx/ssl" "$PRESERVE_ROOT/nginx/ssl"
fi

print_info 'Cleaning previous application files...'
find "$PROJECT_DIR" -mindepth 1 -maxdepth 1 -exec rm -rf {} +

print_info 'Extracting uploaded archive...'
tar -xzf "$ARCHIVE_PATH" -C "$PROJECT_DIR"
rm -f "$ARCHIVE_PATH"

if [ -f "$PRESERVE_ROOT/$REMOTE_ENV_FILE" ]; then
    cp "$PRESERVE_ROOT/$REMOTE_ENV_FILE" "$PROJECT_DIR/$REMOTE_ENV_FILE"
fi

if [ -d "$PRESERVE_ROOT/nginx/ssl" ]; then
    mkdir -p "$PROJECT_DIR/nginx"
    rm -rf "$PROJECT_DIR/nginx/ssl"
    cp -a "$PRESERVE_ROOT/nginx/ssl" "$PROJECT_DIR/nginx/ssl"
fi

if [ ! -f "$PROJECT_DIR/$REMOTE_ENV_FILE" ]; then
    print_error "$REMOTE_ENV_FILE is missing on the VPS. Create it once before deploying."
    exit 1
fi

find "$PROJECT_DIR" -type f \( -name '*.sh' -o -name '.env*' \) -exec sed -i 's/\r$//' {} + 2>/dev/null || true
find "$PROJECT_DIR" -type f -name '*.sh' -exec chmod +x {} + 2>/dev/null || true

print_info 'Running VPS deploy script...'
PROJECT_DIR="$PROJECT_DIR" bash "$PROJECT_DIR/deploy.sh"

if [ "$SKIP_HEALTH_CHECK" = "true" ]; then
    print_info 'Skipping post-deploy HTTP verification as requested.'
    exit 0
fi

print_info 'Running post-deploy verification...'
if command -v curl >/dev/null 2>&1; then
    status_code="$(curl -s -o /dev/null -w '%{http_code}' http://localhost/health/ || true)"
    if [ "$status_code" != '200' ]; then
        print_error "HTTP health check failed with status $status_code"
        exit 1
    fi
fi

print_info 'Deployment completed successfully.'
'@

Write-Step "Deploying and rolling out the new release on the VPS..."
$noBackupValue = if ($NoBackup.IsPresent) { "true" } else { "false" }
$skipHealthValue = if ($SkipHealthCheck.IsPresent) { "true" } else { "false" }

$remoteScript | ssh -o ConnectTimeout=20 -o StrictHostKeyChecking=no "${VpsUser}@${VpsHost}" "bash -s -- '$RemoteArchivePath' '$VpsProjectDir' '$RemoteEnvFile' '$noBackupValue' '$skipHealthValue'"
if ($LASTEXITCODE -ne 0) {
    Write-Warn "Remote deployment failed. Collecting VPS diagnostics..."

    $diagnosticCmd = "cd $VpsProjectDir && " +
        "if docker compose version >/dev/null 2>&1; then " +
        "docker compose -f docker-compose.prod.yml ps; " +
        "echo ''; echo '--- web logs (tail 120) ---'; docker compose -f docker-compose.prod.yml logs --tail=120 web; " +
        "echo ''; echo '--- db logs (tail 120) ---'; docker compose -f docker-compose.prod.yml logs --tail=120 db; " +
        "else " +
        "docker-compose -f docker-compose.prod.yml ps; " +
        "echo ''; echo '--- web logs (tail 120) ---'; docker-compose -f docker-compose.prod.yml logs --tail=120 web; " +
        "echo ''; echo '--- db logs (tail 120) ---'; docker-compose -f docker-compose.prod.yml logs --tail=120 db; " +
        "fi"

    ssh -o ConnectTimeout=20 -o StrictHostKeyChecking=no "${VpsUser}@${VpsHost}" $diagnosticCmd
    Fail "Remote deployment failed."
}

Write-Step "Fetching container status from the VPS..."
Invoke-NativeCommand -FilePath "ssh" -Arguments @(
    "-o", "ConnectTimeout=20",
    "-o", "StrictHostKeyChecking=no",
    "${VpsUser}@${VpsHost}",
    "cd $VpsProjectDir && if docker compose version >/dev/null 2>&1; then docker compose -f docker-compose.prod.yml ps; else docker-compose -f docker-compose.prod.yml ps; fi"
)

Write-Info "Cleaning up the local archive..."
Remove-Item -Path $TempRoot -Recurse -Force

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deployment Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend: http://$VpsHost" -ForegroundColor Green
Write-Host "API:      http://$VpsHost/api" -ForegroundColor Green
Write-Host "Admin:    http://$VpsHost/admin" -ForegroundColor Green
Write-Host ""
Write-Host "Logs:" -ForegroundColor Yellow
$logsHint = "  ssh {0}@{1} 'cd {2} && if docker compose version >/dev/null 2>&1; then docker compose -f docker-compose.prod.yml logs -f; else docker-compose -f docker-compose.prod.yml logs -f; fi'" -f $VpsUser, $VpsHost, $VpsProjectDir
Write-Host $logsHint
