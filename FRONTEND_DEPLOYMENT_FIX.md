# 🚨 URGENT: Frontend Deployment Fix

## Problem
The `docker-compose.prod.yml` was missing the frontend service, so nginx was trying to proxy to a non-existent container. That's why you're seeing the old Django dashboard.

## ✅ What Was Fixed

1. **Added frontend service** to `docker-compose.prod.yml`
   - Builds from `frontend/Dockerfile`
   - Exposes on port 3000
   - Includes all required environment variables
   - Health checks enabled

2. **Updated nginx configuration**
   - Better Next.js static file handling
   - Image optimization support
   - Proper caching headers

## 🚀 Deploy the Fix (2 Methods)

### Method 1: Automatic via GitHub (Recommended)

```bash
# On your local machine
git add .
git commit -m "Fix: Add frontend service to production docker-compose"
git push origin main
```

**Then wait 3-5 minutes** for GitHub Actions to deploy automatically.

Monitor: https://github.com/onyangowanga/COMS-Construction-Operations-Management-System-/actions

---

### Method 2: Manual Deployment (Faster)

If you want to deploy immediately without waiting for GitHub Actions:

```bash
# SSH to your VPS
ssh root@156.232.88.156

# Navigate to project
cd /root/coms

# Pull latest changes
git pull origin main

# Stop all containers
docker-compose -f docker-compose.prod.yml down

# Build frontend image
docker-compose -f docker-compose.prod.yml build frontend

# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Verify all containers are running
docker-compose -f docker-compose.prod.yml ps

# Check frontend logs
docker-compose -f docker-compose.prod.yml logs -f frontend
```

## 🔍 Verify Deployment

### 1. Check Running Containers

```bash
docker ps --filter "name=coms"
```

**You should see 5 containers:**
- ✅ `coms_postgres_prod`
- ✅ `coms_redis_prod`
- ✅ `coms_web_prod` (Django backend)
- ✅ `coms_frontend_prod` (Next.js) ← **This should now exist!**
- ✅ `coms_nginx_prod`

### 2. Check Frontend Container Status

```bash
# Check if frontend is running
docker inspect coms_frontend_prod | grep Status

# Should show: "Status": "running"
```

### 3. Test Frontend Access

```bash
# From VPS, test if frontend is responding
curl http://localhost:3000

# Should return HTML from Next.js
```

### 4. Test via Browser

Visit: **http://156.232.88.156**

You should now see:
- ✅ Modern Next.js frontend (not Django admin)
- ✅ Login page with clean design
- ✅ Sidebar navigation after login
- ✅ Dashboard with KPI cards

### 5. Clear Browser Cache (Important!)

If you still see the old page:
- **Chrome/Edge**: Ctrl + Shift + R (Windows) or Cmd + Shift + R (Mac)
- **Firefox**: Ctrl + F5
- **Or**: Open in Incognito/Private mode

## 🐛 If Frontend Still Not Working

### Check Frontend Logs

```bash
docker-compose -f docker-compose.prod.yml logs frontend
```

**Common issues:**

**1. Build errors:**
```bash
# Rebuild without cache
docker-compose -f docker-compose.prod.yml build --no-cache frontend
docker-compose -f docker-compose.prod.yml up -d frontend
```

**2. Container exits immediately:**
```bash
# Check what went wrong
docker logs coms_frontend_prod

# Common cause: Missing .env variables
# Check frontend/.env.production exists on VPS
```

**3. Nginx 502 Bad Gateway:**
```bash
# Restart nginx
docker-compose -f docker-compose.prod.yml restart nginx

# Check nginx can reach frontend
docker-compose -f docker-compose.prod.yml exec nginx ping frontend
```

**4. Port conflict:**
```bash
# Check if port 3000 is already in use
netstat -tulpn | grep 3000

# If yes, stop the conflicting service
```

## 📊 What Changed in Production

### Before (Old Setup)
```
Internet → Nginx → Django (Templates) → Old Dashboard
```

### After (New Setup)
```
Internet → Nginx
           ├─ / → Next.js Frontend (New Dashboard) ✨
           ├─ /api → Django Backend (REST API)
           ├─ /admin → Django Admin
           └─ /static, /media → Static files
```

## ✅ Success Indicators

After deployment, you should see:

**In Browser (http://156.232.88.156):**
- Modern login page (not Django admin login)
- Next.js branding
- Tailwind CSS styling
- Fast page loads
- No console errors (F12 → Console)

**In Docker:**
```bash
$ docker ps --filter "name=coms_frontend"
CONTAINER ID   IMAGE                  STATUS        PORTS
abc123def456   coms_frontend:latest   Up 2 minutes  3000/tcp
```

**In Logs:**
```bash
$ docker-compose -f docker-compose.prod.yml logs frontend | tail -5
coms_frontend_prod | ▲ Next.js 14.1.0
coms_frontend_prod | - Local:        http://localhost:3000
coms_frontend_prod | - Network:      http://0.0.0.0:3000
coms_frontend_prod | ✓ Ready in 1.2s
```

## 🎯 Quick Deploy Commands

```bash
# Choose one method:

# Method 1: Auto-deploy (from local machine)
git add . && git commit -m "Fix: Add frontend to production" && git push origin main

# Method 2: Manual deploy (on VPS)
ssh root@156.232.88.156 "cd /root/coms && git pull && docker-compose -f docker-compose.prod.yml down && docker-compose -f docker-compose.prod.yml up -d --build"
```

## 📞 Need Help?

If you still see the old dashboard after following these steps:

1. **Check container status**: `docker ps --filter "name=coms"`
2. **View all logs**: `docker-compose -f docker-compose.prod.yml logs`
3. **Restart everything**: `docker-compose -f docker-compose.prod.yml restart`

---

**The fix is ready!** Just deploy using one of the methods above. 🚀
