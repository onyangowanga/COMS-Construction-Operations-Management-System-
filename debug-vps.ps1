# Debug VPS Deployment Issues
param(
    [string]$VpsHost = "156.232.88.156",
    [string]$VpsUser = "root"
)

$ErrorActionPreference = "Continue"

function Write-Section {
    param([string]$Title)
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host $Title -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
}

function Run-SshCommand {
    param([string]$Command)
    ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 "${VpsUser}@${VpsHost}" $Command
}

Write-Host "🔍 COMS VPS Debugging Script" -ForegroundColor Magenta
Write-Host "Target: ${VpsHost}" -ForegroundColor Magenta

Write-Section "1. SSH Connection Test"
Write-Host "Testing SSH connection..."
Run-SshCommand "echo 'SSH Connection: OK'" | Out-String

Write-Section "2. Docker Status"
Write-Host "Checking Docker installation and daemon:"
Run-SshCommand "docker --version && docker ps" | Out-String

Write-Section "3. Docker Compose Status"
Write-Host "Checking docker-compose:"
Run-SshCommand "docker-compose --version" | Out-String

Write-Section "4. Project Directory"
Write-Host "Checking /root/coms directory:"
Run-SshCommand "ls -la /root/coms/ | head -20" | Out-String

Write-Section "5. .env.production File"
Write-Host "Checking if .env.production exists:"
Run-SshCommand "[ -f /root/coms/.env.production ] && echo '.env.production EXISTS' || echo '.env.production MISSING'" | Out-String

Write-Section "6. Running Containers"
Write-Host "List all running containers:"
Run-SshCommand "docker ps -a --no-trunc" | Out-String

Write-Section "7. Docker Compose Config"
Write-Host "Checking docker-compose configuration:"
Run-SshCommand "cd /root/coms && docker-compose -f docker-compose.prod.yml config | head -50" | Out-String

Write-Section "8. Container Logs (last 50 lines each)"

$containers = @("coms_web_prod", "coms_frontend_prod", "coms_nginx_prod", "coms_postgres_prod", "coms_redis_prod")

foreach ($container in $containers) {
    Write-Host "`n--- $container ---" -ForegroundColor Yellow
    Run-SshCommand "docker logs --tail 50 $container 2>&1" | Out-String
}

Write-Section "9. Network Status"
Write-Host "Checking if port 80 is listening:"
Run-SshCommand "netstat -tlnp | grep ':80' || ss -tlnp | grep ':80'" | Out-String

Write-Section "10. Health Check"
Write-Host "Testing HTTP connectivity:"
Run-SshCommand "curl -v http://localhost/ || echo 'HTTP request failed'" | Out-String

Write-Section "11. Nginx Configuration Test"
Write-Host "Testing nginx configuration:"
Run-SshCommand "docker exec coms_nginx_prod nginx -t" | Out-String

Write-Host "`n" -ForegroundColor Green
Write-Host "✓ Debug report complete. Review the output above to identify the issue." -ForegroundColor Green
Write-Host "`nCommon issues:" -ForegroundColor Yellow
Write-Host "  • .env.production is MISSING - copy it to the VPS" -ForegroundColor Yellow
Write-Host "  • Containers are in 'exited' state - check container logs" -ForegroundColor Yellow
Write-Host "  • PostgreSQL connection errors - check DB credentials in .env.production" -ForegroundColor Yellow
Write-Host "  • 'Port 80 in use' - another service is using port 80" -ForegroundColor Yellow
