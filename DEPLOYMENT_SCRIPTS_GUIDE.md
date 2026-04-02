# COMS Deployment Scripts Guide

This guide explains all deployment options available for your COMS application.

## Available Deployment Scripts

### 1. Full Deployment (Backend + Frontend)
Deploys the entire application (Django backend + Next.js frontend)

**PowerShell (Windows):**
```powershell
.\deploy_to_vps.ps1
```

**On VPS directly:**
```bash
./deploy.sh
```

This is the only supported full-deployment entry point from a local machine.

---

### 2. Backend Only Deployment
Deploys only the Django backend (API + Admin)

**PowerShell (Windows):**
```powershell
.\deploy_backend_only.ps1
```

**On VPS directly:**
```bash
./deploy_backend.sh
```

**What it does:**
- Stops and rebuilds only the `web` container
- Runs database migrations
- Collects static files
- Restarts backend without touching frontend

**Use when:**
- You only changed Python/Django code
- Updated API endpoints
- Modified database models
- Changed backend configurations

---

### 3. Frontend Only Deployment
Deploys only the Next.js frontend

**PowerShell (Windows):**
```powershell
.\deploy_frontend_only.ps1
```

**On VPS directly:**
```bash
./deploy_frontend.sh
```

**What it does:**
- Stops and rebuilds only the `frontend` container
- Restarts nginx to pick up changes
- Creates backup of previous frontend
- Keeps backend running

**Use when:**
- You only changed React/Next.js code
- Updated UI components
- Modified frontend styling
- Changed frontend configurations

---

## Quick Reference

| Change Type | Script to Use | Command |
|------------|---------------|---------|
| Backend + Frontend | Full deployment | `.\deploy_to_vps.ps1` |
| Python/Django only | Backend only | `.\deploy_backend_only.ps1` |
| React/Next.js only | Frontend only | `.\deploy_frontend_only.ps1` |
| Database models | Backend only | `.\deploy_backend_only.ps1` |
| UI components | Frontend only | `.\deploy_frontend_only.ps1` |
| API endpoints | Backend only | `.\deploy_backend_only.ps1` |
| Styling/CSS | Frontend only | `.\deploy_frontend_only.ps1` |
| Both changed | Full deployment | `.\deploy_to_vps.ps1` |

---

## Prerequisites

### One-Time Setup

1. **SSH Access configured:**
   ```powershell
   # Test SSH connection
   ssh root@156.232.88.156 'echo "Connection OK"'
   ```

2. **VPS has required tools:**
   ```bash
   ssh root@156.232.88.156
   apt-get update
   apt-get install -y docker.io docker-compose unzip dos2unix
   ```

3. **Project exists on VPS:**
   ```bash
   ssh root@156.232.88.156
   cd /root/coms
   # Create .env.production if not exists
   cp .env.production.example .env.production
   nano .env.production  # Edit with your values
   ```

---

## Deployment Workflows

### Scenario 1: API Changes Only

You modified some Django views or serializers:

```powershell
# 1. Test locally
docker-compose up -d
docker-compose exec web python manage.py test

# 2. Deploy backend only
.\deploy_backend_only.ps1

# 3. Verify
# Visit http://156.232.88.156/api to test
```

**Time saved:** ~60% faster than full deployment

---

### Scenario 2: UI Changes Only

You updated some React components or styling:

```powershell
# 1. Test locally
cd frontend
npm run dev

# 2. Deploy frontend only
cd ..
.\deploy_frontend_only.ps1

# 3. Verify
# Visit http://156.232.88.156
```

**Time saved:** ~70% faster than full deployment

---

### Scenario 3: Database Model Changes

You added/modified Django models:

```powershell
# 1. Create migrations locally
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

# 2. Deploy backend (includes migrations)
.\deploy_backend_only.ps1
```

---

### Scenario 4: Full Stack Changes

You changed both backend and frontend:

```powershell
# Deploy everything
.\deploy_to_vps.ps1
```

---

## Script Details

### deploy_to_vps.ps1 (Full Deployment)

**Steps:**
1. Creates staging directory
2. Copies all project files (excludes node_modules, .git, etc.)
3. Creates ZIP archive
4. Uploads to VPS
5. Extracts on VPS
6. Fixes line endings (Windows → Unix)
7. Runs full deployment script
8. Builds all Docker containers
9. Runs migrations
10. Collects static files
11. Verifies health

**Duration:** ~5-10 minutes (depending on connection speed)

---

### deploy_backend_only.ps1

**Steps:**
1. Copies only backend files (Python, config, apps, api)
2. Uploads to VPS
3. Stops web container
4. Rebuilds web container
5. Runs migrations
6. Collects static files
7. Verifies backend health

**Duration:** ~2-3 minutes

**Files synced:**
- `*.py`
- `requirements.txt`
- `Dockerfile`
- `config/`
- `apps/`
- `api/`

---

### deploy_frontend_only.ps1

**Steps:**
1. Copies only frontend directory
2. Uploads to VPS
3. Creates backup of current frontend
4. Stops frontend container
5. Rebuilds frontend container
6. Restarts nginx
7. Verifies frontend

**Duration:** ~2-4 minutes

**Files synced:**
- `frontend/` directory (excluding node_modules, .next)

---

## Troubleshooting

### Deployment Fails

**Check VPS connection:**
```powershell
ssh root@156.232.88.156 'docker ps'
```

**Check logs:**
```bash
# All containers
ssh root@156.232.88.156 'cd /root/coms && docker-compose -f docker-compose.prod.yml logs --tail=50'

# Backend only
ssh root@156.232.88.156 'cd /root/coms && docker-compose -f docker-compose.prod.yml logs web'

# Frontend only
ssh root@156.232.88.156 'cd /root/coms && docker-compose -f docker-compose.prod.yml logs frontend'
```

---

### Backend Issues

**Container not starting:**
```bash
ssh root@156.232.88.156
cd /root/coms
docker-compose -f docker-compose.prod.yml logs web
docker-compose -f docker-compose.prod.yml restart web
```

**Migration errors:**
```bash
ssh root@156.232.88.156
cd /root/coms
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --plan
docker-compose -f docker-compose.prod.yml exec web python manage.py showmigrations
```

**Permission errors:**
```bash
ssh root@156.232.88.156
cd /root/coms
docker-compose -f docker-compose.prod.yml exec web ls -la /app/logs
# Fix: docker-compose -f docker-compose.prod.yml exec web chmod -R 777 /app/logs
```

---

### Frontend Issues

**Container not starting:**
```bash
ssh root@156.232.88.156
cd /root/coms
docker-compose -f docker-compose.prod.yml logs frontend
docker-compose -f docker-compose.prod.yml restart frontend
```

**Nginx not serving frontend:**
```bash
ssh root@156.232.88.156
cd /root/coms
docker-compose -f docker-compose.prod.yml restart nginx
docker-compose -f docker-compose.prod.yml logs nginx
```

**Build errors:**
```bash
# Rebuild with verbose output
ssh root@156.232.88.156
cd /root/coms
docker-compose -f docker-compose.prod.yml build --no-cache frontend
```

---

### Line Ending Issues

If you see `$'\r': command not found`:

The scripts now automatically fix this, but if issues persist:

```bash
ssh root@156.232.88.156
cd /root/coms

# Fix manually
find . -name "*.sh" -exec dos2unix {} \;
find . -name ".env*" -exec dos2unix {} \;
chmod +x *.sh
```

---

## Advanced Usage

### Deploy with Specific Tag/Version

```bash
ssh root@156.232.88.156
cd /root/coms
git checkout v1.2.3  # or specific commit
./deploy.sh
```

---

### Rollback Deployment

**Frontend rollback:**
```bash
ssh root@156.232.88.156
cd /root/coms

# List backups
ls -la frontend.backup.*

# Restore
rm -rf frontend
mv frontend.backup.20260324_120000 frontend
docker-compose -f docker-compose.prod.yml restart frontend nginx
```

**Backend rollback:**
```bash
ssh root@156.232.88.156
cd /root/coms

# Use git to revert
git log --oneline -10
git checkout <commit-hash>
./deploy_backend.sh
```

---

### Manual Container Management

```bash
ssh root@156.232.88.156
cd /root/coms

# Stop all
docker-compose -f docker-compose.prod.yml down

# Start all
docker-compose -f docker-compose.prod.yml up -d

# Restart specific service
docker-compose -f docker-compose.prod.yml restart web
docker-compose -f docker-compose.prod.yml restart frontend

# View logs
docker-compose -f docker-compose.prod.yml logs -f web
docker-compose -f docker-compose.prod.yml logs -f frontend

# Execute commands
docker-compose -f docker-compose.prod.yml exec web python manage.py shell
docker-compose -f docker-compose.prod.yml exec frontend sh
```

---

## Performance Tips

1. **Use partial deployments** when possible:
   - Backend only: 60% faster
   - Frontend only: 70% faster

2. **Deploy during low-traffic periods** for full deployments

3. **Test locally first** to catch issues early:
   ```powershell
   docker-compose up -d
   docker-compose exec web python manage.py test
   ```

4. **Monitor deployment**:
   ```bash
   # In separate terminal during deployment
   ssh root@156.232.88.156 'cd /root/coms && watch -n 2 docker-compose -f docker-compose.prod.yml ps'
   ```

---

## Security Notes

1. **SSH Keys:** Use SSH keys instead of passwords
2. **Firewall:** Ensure UFW is configured
3. **HTTPS:** Set up SSL certificates for production
4. **Backups:** Implement automated database backups
5. **Secrets:** Never commit `.env.production` to git

---

## Support

**View application status:**
```bash
ssh root@156.232.88.156 'cd /root/coms && docker-compose -f docker-compose.prod.yml ps'
```

**Health checks:**
- Backend: http://156.232.88.156/health/
- Frontend: http://156.232.88.156
- Admin: http://156.232.88.156/admin

**Need help?**
- Check logs first
- Review this guide
- Verify VPS connectivity
- Ensure Docker is running
