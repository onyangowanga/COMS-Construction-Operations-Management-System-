# 🚀 COMS Production Deployment Checklist

Use this checklist to ensure your COMS application is ready for production deployment.

---

## 📋 Pre-Deployment Checklist

### 1. Local Development Complete
- [ ] All features tested locally
- [ ] Frontend builds without errors (`npm run build`)
- [ ] Backend tests pass
- [ ] No console errors in browser
- [ ] All environment variables configured

### 2. VPS Setup
- [ ] VPS accessible via SSH
- [ ] Docker installed on VPS
- [ ] Docker Compose installed on VPS
- [ ] Git installed on VPS
- [ ] Firewall configured (ports 80, 443, 22 open)
- [ ] Repository cloned to `/root/coms`

### 3. Environment Configuration
- [ ] `.env.production` created on VPS
- [ ] `SECRET_KEY` generated and set
- [ ] Database credentials configured
- [ ] `ALLOWED_HOSTS` includes VPS IP/domain
- [ ] Frontend `NEXT_PUBLIC_API_URL` points to VPS
- [ ] Email configuration (if using email features)
- [ ] CORS settings configured

### 4. GitHub Configuration
- [ ] GitHub repository accessible
- [ ] GitHub Secrets configured:
  - [ ] `VPS_HOST`
  - [ ] `VPS_USERNAME`
  - [ ] `VPS_PASSWORD` or `VPS_SSH_KEY`
- [ ] CI/CD workflow file exists (`.github/workflows/ci-cd.yml`)

### 5. Security
- [ ] Strong passwords used for:
  - [ ] Database
  - [ ] Django SECRET_KEY
  - [ ] VPS root
- [ ] `DEBUG=False` in production
- [ ] HTTPS configured (or planned post-deployment)
- [ ] Firewall enabled
- [ ] SSH key-based authentication (recommended)

---

## 🎯 Initial Deployment Steps

### Step 1: VPS Initial Setup
```bash
# SSH into VPS
ssh root@156.232.88.156

# Navigate to project directory
cd /root/coms

# Verify .env.production exists
ls -la .env.production

# Make deployment script executable
chmod +x deploy.sh
```

### Step 2: Run Initial Deployment
```bash
# Run deployment script
./deploy.sh
```

**Expected output:**
```
================================
COMS Deployment Script
================================

[INFO] Navigating to project directory...
[INFO] Pulling latest changes from GitHub...
[INFO] Loading environment variables...
[INFO] Stopping existing containers...
[INFO] Cleaning up orphaned containers...
[INFO] Building Docker images...
[INFO] Starting containers...
[INFO] Waiting for services to start...
[INFO] Running database migrations...
[INFO] Collecting static files...
[INFO] Verifying frontend container...
[INFO] Checking container status...
[INFO] Testing application health...
[INFO] Deployment successful! Application is healthy.
```

### Step 3: Create Superuser
```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

Enter credentials when prompted.

### Step 4: Verify Containers Running
```bash
docker ps --filter "name=coms"
```

**Should show 5 running containers:**
- `coms_postgres_prod`
- `coms_redis_prod`
- `coms_web_prod`
- `coms_frontend_prod`
- `coms_nginx_prod`

### Step 5: Test Application
```bash
# Test health endpoint
curl http://localhost/health/

# Test API
curl http://localhost/api/

# Test frontend
curl http://localhost/
```

All should return success (200 status codes).

### Step 6: Access from Browser
Visit: **http://156.232.88.156**

- [ ] Frontend loads correctly
- [ ] Can navigate to login page
- [ ] Can log in with superuser credentials
- [ ] Dashboard displays
- [ ] Navigation works
- [ ] No console errors

---

## 🔄 Post-Deployment Verification

### Frontend Checks
- [ ] Home page loads
- [ ] Login page accessible
- [ ] Can log in successfully
- [ ] Dashboard shows data
- [ ] Sidebar navigation works
- [ ] All menu items accessible (based on permissions)
- [ ] No 404 errors on page refresh
- [ ] API calls working (check Network tab)
- [ ] WebSocket connections (if applicable)

### Backend Checks
- [ ] Django Admin accessible at `/admin`
- [ ] Can log into Django Admin
- [ ] API endpoints responding at `/api`
- [ ] Database queries working
- [ ] Static files serving correctly
- [ ] Media files uploading/downloading
- [ ] Permissions system working

### Performance Checks
- [ ] Page load time < 3 seconds
- [ ] API response time < 1 second
- [ ] No memory leaks (check `docker stats`)
- [ ] CPU usage stable
- [ ] Database queries optimized

### Security Checks
- [ ] HTTPS enabled (or HTTP→HTTPS redirect disabled until SSL setup)
- [ ] Django Admin requires authentication
- [ ] API requires authentication
- [ ] CORS properly configured
- [ ] No sensitive data in frontend code
- [ ] Environment variables not exposed
- [ ] XSS protection headers present
- [ ] CSRF protection enabled

---

## 🔐 Security Hardening (Post-Deployment)

### Enable HTTPS (Recommended)
```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Get SSL certificate (requires domain name)
certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Update `.env.production`:
```env
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
NEXT_PUBLIC_API_URL=https://yourdomain.com/api
NEXT_PUBLIC_WS_URL=wss://yourdomain.com/ws
```

### Set Up Automated Backups
```bash
# Create backup directory
mkdir -p /root/coms-backups

# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * cd /root/coms && docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U coms_user coms_production > /root/coms-backups/backup_$(date +\%Y\%m\%d_\%H\%M\%S).sql

# Delete backups older than 7 days
0 3 * * * find /root/coms-backups/ -name "backup_*.sql" -mtime +7 -delete
```

### Configure Firewall
```bash
# Install UFW
apt install ufw -y

# Allow SSH, HTTP, HTTPS
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp

# Enable
ufw enable

# Verify
ufw status
```

### Update Environment for Production
In `.env.production`:
```env
DEBUG=False
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

---

## 🔄 GitHub Auto-Deployment Workflow

### How It Works
1. Developer pushes to `main` branch
2. GitHub Actions triggered automatically
3. Runs backend tests (Django)
4. Runs frontend tests (TypeScript, ESLint, build)
5. Builds Docker images (test build)
6. SSH into VPS and runs `deploy.sh`
7. Verifies deployment health
8. Sends notification

### Verify Auto-Deployment
```bash
# Make a small change locally
echo "# Test deployment" >> README.md

# Commit and push
git add .
git commit -m "Test auto-deployment"
git push origin main

# Monitor on GitHub
# Go to: https://github.com/onyangowanga/COMS-Construction-Operations-Management-System-/actions

# Monitor on VPS
ssh root@156.232.88.156
cd /root/coms
docker-compose -f docker-compose.prod.yml logs -f
```

---

## 📊 Monitoring Setup

### View Logs
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f frontend
docker-compose -f docker-compose.prod.yml logs -f web
docker-compose -f docker-compose.prod.yml logs -f nginx

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100
```

### Monitor Resources
```bash
# Real-time container stats
docker stats

# Disk usage
df -h

# Memory usage
free -h

# System load
htop
```

### Health Checks
```bash
# Application health
curl http://localhost/health/

# Database connection
docker-compose -f docker-compose.prod.yml exec db pg_isready -U coms_user -d coms_production

# Redis connection
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping
```

---

## 🐛 Common Issues & Solutions

### Issue: Containers Not Starting
**Solution:**
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs

# Rebuild
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

### Issue: Frontend Shows 502 Bad Gateway
**Solution:**
```bash
# Check frontend logs
docker-compose -f docker-compose.prod.yml logs frontend

# Restart frontend
docker-compose -f docker-compose.prod.yml restart frontend
```

### Issue: Database Migration Errors
**Solution:**
```bash
# Reset migrations (⚠️ only on fresh deployment)
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --fake

# Or run migrations manually
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
```

### Issue: Static Files Not Loading
**Solution:**
```bash
# Recollect static files
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Restart nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

---

## 📅 Maintenance Schedule

### Daily
- [ ] Check application is accessible
- [ ] Monitor error logs
- [ ] Verify automated backups ran

### Weekly
- [ ] Review application logs for errors
- [ ] Check disk space usage
- [ ] Test backup restoration
- [ ] Update dependencies (security patches)

### Monthly
- [ ] Full backup and download to local
- [ ] Review and rotate old backups
- [ ] Performance audit
- [ ] Security audit
- [ ] Update Docker images

---

## 🎯 Performance Optimization (Optional)

### Enable Redis Caching
In Django settings, configure Redis for caching:
```python
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
    }
}
```

### Enable Nginx Caching
Add to nginx config:
```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=1g;

location /api/ {
    proxy_cache api_cache;
    proxy_cache_valid 200 5m;
    # ... rest of config
}
```

### Database Optimization
```bash
# Run VACUUM on database
docker-compose -f docker-compose.prod.yml exec db psql -U coms_user -d coms_production -c "VACUUM ANALYZE;"
```

---

## ✅ Final Checklist

Before marking deployment as complete:

### Technical
- [ ] All containers running
- [ ] Application accessible from internet
- [ ] Database migrations applied
- [ ] Static files serving
- [ ] Superuser account created
- [ ] HTTPS configured (or planned)
- [ ] Backups configured
- [ ] Monitoring set up

### Functional
- [ ] Can log in as admin
- [ ] All pages load correctly
- [ ] CRUD operations work
- [ ] Permissions enforced correctly
- [ ] No JavaScript errors
- [ ] No 500 errors in logs

### Security
- [ ] Firewall enabled
- [ ] Strong passwords used
- [ ] DEBUG=False
- [ ] Security headers present
- [ ] CORS configured
- [ ] SSH keys (recommended)

### Operations
- [ ] Auto-deployment tested
- [ ] Backup/restore tested
- [ ] Rollback procedure documented
- [ ] Contact information updated
- [ ] Team trained on deployment

---

**Production deployment complete!** 🎉

**Access Points:**
- **Frontend**: http://156.232.88.156
- **Admin**: http://156.232.88.156/admin
- **API**: http://156.232.88.156/api

**Support:**
- GitHub: https://github.com/onyangowanga/COMS-Construction-Operations-Management-System-
- Workflows: https://github.com/onyangowanga/COMS-Construction-Operations-Management-System-/actions
