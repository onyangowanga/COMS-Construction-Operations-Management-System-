# Deploy COMS from Local to VPS

This workflow deploys directly from your local machine to the VPS over SSH. It does not depend on GitHub Actions or any git push on the server.

## Deployment Model

The supported path is now:

1. Build a clean tar archive locally.
2. Upload that archive to the VPS with `scp`.
3. Preserve VPS-only files such as `.env.production` and `nginx/ssl`.
4. Replace the application files on the VPS.
5. Run `deploy.sh` on the VPS to rebuild and restart Docker services.
6. Verify container state and the `/health/` endpoint.

This gives you a simple local-to-server CI/CD path without relying on git on the VPS.

## Prerequisites

1. SSH access to `root@156.232.88.156`.
2. `ssh`, `scp`, and `tar.exe` available on your Windows machine.
3. Docker and either `docker compose` or `docker-compose` installed on the VPS.
4. A production env file already created on the VPS at `/root/coms/.env.production`.

## One-Time VPS Setup

SSH into the VPS and prepare the app directory once:

```bash
ssh root@156.232.88.156
mkdir -p /root/coms
cd /root/coms
```

Create the production env file:

```bash
cp .env.production.example .env.production
nano .env.production
```

If you terminate TLS on the VPS with local cert files, keep them under `/root/coms/nginx/ssl`. The deployment script preserves that directory.

## Windows Deployment

Run the deployment from the COMS project folder:

```powershell
cd "C:\programing\Realtime projects\COMS\COMS PROJECT IMPLEMENTATTION\COMS"
.\deploy_to_vps.ps1
```

Optional flags:

```powershell
.\deploy_to_vps.ps1 -NoBackup
.\deploy_to_vps.ps1 -SkipHealthCheck
.\deploy_to_vps.ps1 -VpsHost 156.232.88.156 -VpsUser root -VpsProjectDir /root/coms
```

## What the Script Preserves

The local archive excludes transient and server-only files, including:

- `.git`
- `.github`
- `.venv`
- `node_modules`
- `.next`
- `postgres_data`
- `redis_data`
- `staticfiles`
- `media`
- `logs`
- `.env.production`

On the VPS, the script explicitly preserves:

- `.env.production`
- `nginx/ssl`

## What the Script Does

1. Validates that local `ssh`, `scp`, and `tar.exe` exist.
2. Validates SSH connectivity to the VPS.
3. Creates a deployment archive from your local source tree.
4. Uploads the archive to `/tmp` on the VPS.
5. Stops existing containers.
6. Backs up the current VPS env file and SSL directory unless `-NoBackup` is used.
7. Replaces the deployed application files.
8. Runs `deploy.sh`.
9. Prints the resulting container status.

## Verifying Deployment

Check running services:

```bash
ssh root@156.232.88.156 'cd /root/coms && if docker compose version >/dev/null 2>&1; then docker compose -f docker-compose.prod.yml ps; else docker-compose -f docker-compose.prod.yml ps; fi'
```

View logs:

```bash
ssh root@156.232.88.156 'cd /root/coms && if docker compose version >/dev/null 2>&1; then docker compose -f docker-compose.prod.yml logs -f; else docker-compose -f docker-compose.prod.yml logs -f; fi'
```

Check health manually:

```bash
ssh root@156.232.88.156 'curl -I http://localhost/health/'
```

## Troubleshooting

### SSH connection fails

Test connectivity directly:

```bash
ssh root@156.232.88.156 'echo ok'
```

If that fails, fix SSH before retrying deployment.

### `.env.production` is missing on the VPS

The deploy script will stop rather than guessing production secrets. Create it manually once:

```bash
ssh root@156.232.88.156
cd /root/coms
cp .env.production.example .env.production
nano .env.production
```

### Compose command is different on the VPS

Both `deploy_to_vps.ps1` and `deploy.sh` auto-detect `docker compose` and `docker-compose`.

### Deployment fails after containers start

Inspect the logs:

```bash
ssh root@156.232.88.156 'cd /root/coms && if docker compose version >/dev/null 2>&1; then docker compose -f docker-compose.prod.yml logs --tail=100; else docker-compose -f docker-compose.prod.yml logs --tail=100; fi'
```

### Manual recovery

If you need to rerun the server-side rollout only:

```bash
ssh root@156.232.88.156
cd /root/coms
PROJECT_DIR=/root/coms bash ./deploy.sh
```

## Recommended Workflow

1. Test locally with Docker.
2. Run `deploy_to_vps.ps1`.
3. Confirm the app loads at `http://156.232.88.156`.
4. Check logs only if the health check or UI indicates a problem.