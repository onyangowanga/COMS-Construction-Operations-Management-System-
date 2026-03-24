# COMS Setup Verification Script
# Quick health check for local development environment

Write-Host ""
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "   COMS Local Environment Verification" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""

$allGood = $true

# Check 1: Docker containers
Write-Host "[1/6] Checking Docker containers..." -ForegroundColor Cyan
$containers = docker-compose ps --format json 2>$null | ConvertFrom-Json
$expectedContainers = @("web", "db", "redis", "frontend")
$runningContainers = @()

foreach ($container in $containers) {
    if ($container.State -eq "running") {
        $runningContainers += $container.Service
        Write-Host "  [OK] $($container.Service) is running" -ForegroundColor Green
    } else {
        Write-Host "  [ERROR] $($container.Service) is $($container.State)" -ForegroundColor Red
        $allGood = $false
    }
}

# Check 2: Database connectivity
Write-Host "`n[2/6] Checking database connectivity..." -ForegroundColor Cyan
$dbCheck = docker-compose exec -T db pg_isready -U coms_user -d coms_db 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Database is ready" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] Database is not ready" -ForegroundColor Red
    $allGood = $false
}

# Check 3: Redis connectivity
Write-Host "`n[3/6] Checking Redis connectivity..." -ForegroundColor Cyan
$redisCheck = docker-compose exec -T redis redis-cli ping 2>$null
if ($redisCheck -match "PONG") {
    Write-Host "  [OK] Redis is ready" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] Redis is not responding" -ForegroundColor Red
    $allGood = $false
}

# Check 4: Django health endpoint
Write-Host "`n[4/6] Checking Django backend..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health/" -UseBasicParsing -TimeoutSec 5 2>$null
    if ($response.StatusCode -eq 200) {
        Write-Host "  [OK] Backend API is responding" -ForegroundColor Green
    } else {
        Write-Host "  [WARNING] Backend returned status: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  [ERROR] Cannot reach backend at http://localhost:8000/health/" -ForegroundColor Red
    $allGood = $false
}

# Check 5: Frontend
Write-Host "`n[5/6] Checking Next.js frontend..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5 2>$null
    if ($response.StatusCode -eq 200) {
        Write-Host "  [OK] Frontend is responding" -ForegroundColor Green
    } else {
        Write-Host "  [WARNING] Frontend returned status: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  [ERROR] Cannot reach frontend at http://localhost:3000" -ForegroundColor Red
    $allGood = $false
}

# Check 6: Migrations
Write-Host "`n[6/6] Checking database migrations..." -ForegroundColor Cyan
$migrations = docker-compose exec -T web python manage.py showmigrations --plan 2>$null
if ($LASTEXITCODE -eq 0) {
    $unapplied = $migrations | Select-String "\[ \]"
    if ($unapplied) {
        Write-Host "  [WARNING] Some migrations are not applied" -ForegroundColor Yellow
        Write-Host "  Run: docker-compose exec web python manage.py migrate"
    } else {
        Write-Host "  [OK] All migrations are applied" -ForegroundColor Green
    }
} else {
    Write-Host "  [ERROR] Could not check migrations" -ForegroundColor Red
    $allGood = $false
}

# Summary
Write-Host ""
Write-Host "=======================================================" -ForegroundColor Cyan

if ($allGood) {
    Write-Host "   All checks passed! " -ForegroundColor Green
    Write-Host "=======================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your COMS environment is ready for development!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Access your application:" -ForegroundColor Cyan
    Write-Host "  Frontend:     " -NoNewline
    Write-Host "http://localhost:3000" -ForegroundColor Yellow
    Write-Host "  Backend API:  " -NoNewline
    Write-Host "http://localhost:8000/api" -ForegroundColor Yellow
    Write-Host "  Django Admin: " -NoNewline
    Write-Host "http://localhost:8000/admin" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Create superuser (if not done):" -ForegroundColor White
    Write-Host "     docker-compose exec web python manage.py createsuperuser"
    Write-Host "  2. Start developing!"
    Write-Host "  3. When ready, deploy: .\deploy-local-to-vps.ps1"
    Write-Host ""
} else {
    Write-Host "   Some checks failed " -ForegroundColor Red
    Write-Host "=======================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please review the errors above and fix them." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Common fixes:" -ForegroundColor Cyan
    Write-Host "  - Restart containers: docker-compose restart"
    Write-Host "  - View logs: docker-compose logs -f"
    Write-Host "  - Rebuild: docker-compose down && docker-compose up -d"
    Write-Host ""
}
