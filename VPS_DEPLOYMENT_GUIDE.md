# 🚀 COMS VPS Deployment Guide (TrueHost)

Complete guide for deploying COMS (frontend + backend) to your TrueHost VPS with automatic deployment via GitHub Actions.

---

## 📋 Overview

**Your Setup:**
- **VPS Provider**: TrueHost
- **VPS IP**: 156.232.88.156
- **Hostname**: coms-rsv-02
- **Auto-Deployment**: Enabled via GitHub Actions (pushes to `main` branch)
- **Application Stack**: PostgreSQL, Redis, Django, Next.js, Nginx

**How it works:**
1. You push code to GitHub (`main` branch)
2. GitHub Actions runs tests (backend + frontend)
3. GitHub Actions builds Docker images
4. GitHub Actions connects to your VPS via SSH
5. Deployment script runs automatically
6. Application is updated with zero downtime

---

## 🔧 Prerequisites

### On Your Local Machine
- [x] Git installed
- [x] GitHub repository connected
- [x] Docker Desktop (for local testing)

### On Your VPS (TrueHost)
- [x] Docker installed
- [x] Docker Compose installed
- [x] Git installed
- [x] SSH access enabled
- [x] Port 80 and 443 open

---

## 🛠️ Initial VPS Setup (One-Time)

### 1. SSH into Your VPS

```bash
ssh root@156.232.88.156
```

### 2. Install Required Software

```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y

# Install Git
apt install git -y

# Verify installations
docker --version
docker-compose --version
git --version
```

### 3. Clone Repository

```bash
# Navigate to desired directory
cd /root

# Clone your repository
git clone https://github.com/onyangowanga/COMS-Construction-Operations-Management-System-.git coms

# Navigate to project
cd coms
```

### 4. Create Production Environment File

```bash
# Copy the example file
cp .env.production.example .env.production

# Edit with your actual values
nano .env.production
```

**Required values to update in `.env.production`:**

```env
# Django Settings
SECRET_KEY=<generate-a-long-random-string-here>
DEBUG=False
ALLOWED_HOSTS=156.232.88.156,coms-rsv-02

# Database Configuration
POSTGRES_DB=coms_production
POSTGRES_USER=coms_user
POSTGRES_PASSWORD=<create-strong-password-here>
DATABASE_URL=postgresql://coms_user:<your-password>@db:5432/coms_production

# Redis Configuration
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Frontend Environment Variables
NEXT_PUBLIC_API_URL=http://156.232.88.156/api
NEXT_PUBLIC_WS_URL=ws://156.232.88.156/ws
NEXT_PUBLIC_APP_NAME=COMS
NEXT_PUBLIC_APP_VERSION=1.0.0

# Email Configuration (if using email)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=COMS System <noreply@yourdomain.com>

# Security (can enable HTTPS later)
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

# CORS Settings
CORS_ALLOWED_ORIGINS=http://156.232.88.156
CORS_ALLOW_CREDENTIALS=True
```

**To generate a secure SECRET_KEY:**
```bash
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Save and exit (Ctrl + X, then Y, then Enter).

### 5. Make Deployment Script Executable

```bash
chmod +x deploy.sh
```

### 6. Run Initial Deployment

```bash
./deploy.sh
```

This will:
- Pull latest code
- Build Docker images (backend, frontend, nginx)
- Start all containers
- Run database migrations
- Collect static files
- Verify deployment

### 7. Create Django Superuser

```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

Enter your admin credentials when prompted.

### 8. Verify Deployment

**Check running containers:**
```bash
docker ps
```

You should see:
- `coms_postgres_prod` (PostgreSQL)
- `coms_redis_prod` (Redis)
- `coms_web_prod` (Django backend)
- `coms_frontend_prod` (Next.js frontend)
- `coms_nginx_prod` (Nginx reverse proxy)

**Access your application:**
- **Frontend**: http://156.232.88.156
- **Django Admin**: http://156.232.88.156/admin
- **API**: http://156.232.88.156/api

---

## 🔐 GitHub Secrets Setup (For Auto-Deployment)

For automatic deployment to work, you need to configure GitHub Secrets:

### 1. Go to GitHub Repository Settings

```
https://github.com/onyangowanga/COMS-Construction-Operations-Management-System-/settings/secrets/actions
```

### 2. Add the Following Secrets

Click **"New repository secret"** for each:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `VPS_HOST` | `156.232.88.156` | Your VPS IP address |
| `VPS_USERNAME` | `root` | SSH username |
| `VPS_PASSWORD` | `<your-vps-password>` | SSH password for root |

**Note:** For better security, consider using SSH keys instead of passwords. See "SSH Key Setup" section below.

---

## 🚀 Automatic Deployment Workflow

Once GitHub Secrets are configured, deployment is automatic:

### 1. Make Code Changes Locally

```bash
# Edit files in your project
# Example: Update a component
code frontend/components/ui/Button.tsx
```

### 2. Commit and Push to Main Branch

```bash
git add .
git commit -m "Update Button component styling"
git push origin main
```

### 3. GitHub Actions Runs Automatically

GitHub will:
1. ✅ Run backend tests (Django)
2. ✅ Run frontend tests (TypeScript, ESLint, build)
3. ✅ Build Docker images (test build)
4. ✅ Deploy to VPS (if tests pass)
5. ✅ Verify deployment health

### 4. Monitor Deployment Progress

**On GitHub:**
- Go to: `https://github.com/onyangowanga/COMS-Construction-Operations-Management-System-/actions`
- View the running workflow
- See real-time logs

**On VPS (SSH):**
```bash
# SSH into VPS
ssh root@156.232.88.156

# Navigate to project
cd /root/coms

# Watch deployment logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 5. Verify Update

Visit http://156.232.88.156 and verify your changes are live.

---

## 🔧 Manual Deployment (If Needed)

If automatic deployment fails or you want to deploy manually:

### SSH into VPS

```bash
ssh root@156.232.88.156
cd /root/coms
```

### Run Deployment Script

```bash
./deploy.sh
```

### View Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f frontend
docker-compose -f docker-compose.prod.yml logs -f web
docker-compose -f docker-compose.prod.yml logs -f nginx
```

---

## 📊 Application Management

### View Running Containers

```bash
docker ps
# Or for COMS containers only
docker ps --filter "name=coms"
```

### Restart a Service

```bash
# Restart frontend
docker-compose -f docker-compose.prod.yml restart frontend

# Restart backend
docker-compose -f docker-compose.prod.yml restart web

# Restart nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

### Stop All Services

```bash
docker-compose -f docker-compose.prod.yml down
```

### Start All Services

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Rebuild a Specific Service

```bash
# Rebuild and restart frontend
docker-compose -f docker-compose.prod.yml up -d --build frontend

# Rebuild and restart backend
docker-compose -f docker-compose.prod.yml up -d --build web
```

---

## 🗄️ Database Management

### Create Database Backup

```bash
# Create backup directory
mkdir -p /root/coms-backups

# Backup database
docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U coms_user coms_production > /root/coms-backups/backup_$(date +%Y%m%d_%H%M%S).sql

# List backups
ls -lh /root/coms-backups/
```

### Restore Database Backup

```bash
# Restore from backup file
docker-compose -f docker-compose.prod.yml exec -T db psql -U coms_user coms_production < /root/coms-backups/backup_20260312_120000.sql
```

### Run Django Management Commands

```bash
# Access Django shell
docker-compose -f docker-compose.prod.yml exec web python manage.py shell

# Create superuser
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Run migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Collect static files
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

---

## 🔍 Troubleshooting

### Deployment Fails with Git Error

**Problem:** "Repository not found" or merge conflicts

**Solution:**
```bash
ssh root@156.232.88.156
cd /root/coms
git status
git fetch origin
git reset --hard origin/main
git pull origin main
./deploy.sh
```

### Frontend Container Not Starting

**Problem:** Frontend container exits immediately

**Check logs:**
```bash
docker-compose -f docker-compose.prod.yml logs frontend
```

**Common causes:**
- Missing environment variables
- Node.js build errors
- Port 3000 already in use

**Solution:**
```bash
# Rebuild frontend
docker-compose -f docker-compose.prod.yml build --no-cache frontend
docker-compose -f docker-compose.prod.yml up -d frontend
```

### Backend API Not Responding

**Problem:** `/api` endpoints return 502 Bad Gateway

**Check backend logs:**
```bash
docker-compose -f docker-compose.prod.yml logs web
```

**Check backend container status:**
```bash
docker ps --filter "name=coms_web"
```

**Restart backend:**
```bash
docker-compose -f docker-compose.prod.yml restart web
```

### Nginx Shows Default Page

**Problem:** Visiting IP shows Nginx default page, not COMS

**Check nginx config:**
```bash
docker-compose -f docker-compose.prod.yml exec nginx nginx -t
```

**Restart nginx:**
```bash
docker-compose -f docker-compose.prod.yml restart nginx
```

### Database Connection Errors

**Problem:** "could not connect to server: Connection refused"

**Check database container:**
```bash
docker-compose -f docker-compose.prod.yml exec db pg_isready -U coms_user -d coms_production
```

**Restart database:**
```bash
docker-compose -f docker-compose.prod.yml restart db
```

### Out of Disk Space

**Check disk usage:**
```bash
df -h
```

**Clean Docker:**
```bash
# Remove unused containers, networks, images
docker system prune -a

# Remove old logs
docker-compose -f docker-compose.prod.yml logs --tail=0 -f > /dev/null &
```

---

## 🔒 Security Hardening (Recommended)

### 1. Enable HTTPS with Let's Encrypt

```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Obtain SSL certificate (with domain name)
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Or for IP-based setup (limited)
# You'll need a domain name for proper SSL
```

### 2. Enable Firewall

```bash
# Install UFW
apt install ufw -y

# Allow SSH
ufw allow 22/tcp

# Allow HTTP and HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Enable firewall
ufw enable

# Check status
ufw status
```

### 3. Set Up Automated Backups

Create backup cron job:

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /root/coms && docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U coms_user coms_production > /root/coms-backups/backup_$(date +\%Y\%m\%d_\%H\%M\%S).sql

# Delete backups older than 7 days
0 3 * * * find /root/coms-backups/ -name "backup_*.sql" -mtime +7 -delete
```

### 4. Use SSH Keys Instead of Passwords

On your local machine:

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your-email@example.com"

# Copy to VPS
ssh-copy-id root@156.232.88.156
```

Update GitHub Secrets:
- Remove `VPS_PASSWORD`
- Add `VPS_SSH_KEY` with your private key content

Update `.github/workflows/ci-cd.yml`:
```yaml
- name: Deploy to VPS
  uses: appleboy/ssh-action@v1.0.3
  with:
    host: ${{ secrets.VPS_HOST }}
    username: ${{ secrets.VPS_USERNAME }}
    key: ${{ secrets.VPS_SSH_KEY }}    # Changed from password
    port: 22
    script: |
      cd /root/coms
      ./deploy.sh
```

---

## 📈 Monitoring and Logs

### Real-Time Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Frontend only
docker-compose -f docker-compose.prod.yml logs -f frontend

# Backend only
docker-compose -f docker-compose.prod.yml logs -f web

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100
```

### Container Resource Usage

```bash
docker stats
```

### Application Health

```bash
# Test health endpoint
curl http://localhost/health/

# Test API
curl http://localhost/api/

# Test frontend
curl http://localhost/
```

---

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Deploy manually | `./deploy.sh` |
| View all logs | `docker-compose -f docker-compose.prod.yml logs -f` |
| Restart all | `docker-compose -f docker-compose.prod.yml restart` |
| Stop all | `docker-compose -f docker-compose.prod.yml down` |
| Start all | `docker-compose -f docker-compose.prod.yml up -d` |
| Backup database | `docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U coms_user coms_production > backup.sql` |
| Django shell | `docker-compose -f docker-compose.prod.yml exec web python manage.py shell` |
| Create superuser | `docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser` |
| Check containers | `docker ps --filter "name=coms"` |
| Clean Docker | `docker system prune -a` |

---

## 📞 Support

**Application URLs:**
- Frontend: http://156.232.88.156
- Admin: http://156.232.88.156/admin
- API: http://156.232.88.156/api

**GitHub Actions:**
- Workflows: https://github.com/onyangowanga/COMS-Construction-Operations-Management-System-/actions

**SSH Access:**
```bash
ssh root@156.232.88.156
```

---

## ✅ Deployment Checklist

Before first deployment:
- [ ] VPS software installed (Docker, Docker Compose, Git)
- [ ] Repository cloned to `/root/coms`
- [ ] `.env.production` file created with actual values
- [ ] GitHub Secrets configured (VPS_HOST, VPS_USERNAME, VPS_PASSWORD/VPS_SSH_KEY)
- [ ] Deployment script made executable (`chmod +x deploy.sh`)
- [ ] Initial deployment successful (`./deploy.sh`)
- [ ] Django superuser created
- [ ] Application accessible at http://156.232.88.156

For each deployment:
- [ ] Tests pass locally
- [ ] Changes committed and pushed to `main`
- [ ] GitHub Actions workflow completes successfully
- [ ] Application updates verified on VPS
- [ ] No errors in logs

---

**Your COMS application is now set up for automatic deployment!** Push to `main` branch and watch it deploy automatically. 🎉
