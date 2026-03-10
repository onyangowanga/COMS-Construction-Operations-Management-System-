# 🚀 COMS VPS Deployment - Action Plan

**Your Step-by-Step Guide to Deploy COMS to Your VPS**

---

## ⚡ Phase 1: Commit and Push Setup Files (5 minutes)

### Step 1: Commit All Deployment Files

Open PowerShell in your project directory:

```powershell
cd "c:\programing\Realtime projects\COMS\COMS PROJECT IMPLEMENTATTION\COMS"

# Check what files will be committed
git status

# Add all deployment files
git add .

# Commit
git commit -m "Add production deployment configuration and scripts"

# Push to GitHub
git push origin master
```

**Files being pushed:**
- ✅ `.env.production` (template)
- ✅ `Dockerfile.prod`
- ✅ `docker-compose.prod.yml`
- ✅ `nginx/nginx.conf`
- ✅ `nginx/conf.d/coms.conf`
- ✅ `setup-vps.sh`
- ✅ `deploy.sh`
- ✅ `.github/workflows/ci-cd.yml` (updated)
- ✅ All documentation

---

## ⚡ Phase 2: Configure GitHub Secrets (3 minutes)

### Step 2: Add Secrets to GitHub Repository

1. **Open GitHub Repository Settings:**
   - Go to: https://github.com/onyangowanga/COMS-Construction-Operations-Management-System-/settings/secrets/actions
   - Or navigate: Your Repository → Settings → Secrets and variables → Actions

2. **Add Secret 1 - VPS_HOST:**
   - Click **"New repository secret"**
   - Name: `VPS_HOST`
   - Value: `156.232.88.156`
   - Click **"Add secret"**

3. **Add Secret 2 - VPS_USERNAME:**
   - Click **"New repository secret"**
   - Name: `VPS_USERNAME`
   - Value: `root`
   - Click **"Add secret"**

4. **Add Secret 3 - VPS_PASSWORD:**
   - Click **"New repository secret"**
   - Name: `VPS_PASSWORD`
   - Value: `Coms@0722!`
   - Click **"Add secret"**

✅ **Verification:** You should now see 3 secrets listed.

---

## ⚡ Phase 3: Initial VPS Setup (10-15 minutes)

### Step 3: Connect to Your VPS

**Using PowerShell (Windows):**

```powershell
ssh root@156.232.88.156
```

When prompted for password, enter:
```
Coms@0722!
```

✅ **You should now be connected to your VPS terminal.**

---

### Step 4: Run Initial Setup Script

**Copy and paste this entire command:**

```bash
curl -o setup-vps.sh https://raw.githubusercontent.com/onyangowanga/COMS-Construction-Operations-Management-System-/master/setup-vps.sh && chmod +x setup-vps.sh && ./setup-vps.sh
```

**What happens next:**

1. **System Update** (2-3 minutes)
   - Updates Ubuntu packages
   - Installs essential tools

2. **Docker Installation** (3-4 minutes)
   - Installs Docker Engine
   - Installs Docker Compose
   - Configures Docker to start on boot

3. **Firewall Configuration** (30 seconds)
   - Enables UFW firewall
   - Opens ports 22 (SSH), 80 (HTTP), 443 (HTTPS)

4. **Repository Clone** (30 seconds)
   - Clones your GitHub repository to `/root/coms`

5. **Environment Configuration** (Manual - 2 minutes)
   - Opens nano editor with `.env.production`
   - **IMPORTANT:** The SECRET_KEY will be auto-generated
   - **Review and press Ctrl+X, then Y, then Enter to save**

6. **Docker Build** (5-7 minutes)
   - Builds production Docker images
   - Starts all containers
   - Waits for services to be healthy

7. **Database Setup** (1 minute)
   - Runs database migrations
   - Creates database tables

8. **Superuser Creation** (Manual - 1 minute)
   - **You'll be prompted to create admin account**
   - Choose username (e.g., `admin`)
   - Enter email (e.g., `admin@yourdomain.com`)
   - Create strong password
   - **SAVE THESE CREDENTIALS!**

9. **Static Files** (30 seconds)
   - Collects static files for Nginx

10. **Health Check** (10 seconds)
    - Verifies application is running
    - Tests health endpoint

---

### Step 5: Verify Installation

After setup completes, you should see:

```
================================
Setup completed successfully!
================================

Your COMS application is now running at:
  http://156.232.88.156
```

**Test it:**

1. **Check containers are running:**
   ```bash
   docker ps
   ```
   
   You should see 4 containers:
   - `coms_nginx_prod`
   - `coms_web_prod`
   - `coms_postgres_prod`
   - `coms_redis_prod`

2. **Test health endpoint:**
   ```bash
   curl http://localhost/health/
   ```
   
   Should return: `{"status":"healthy","timestamp":"..."}`

3. **Open in browser:**
   - Visit: http://156.232.88.156
   - You should see the COMS login page!

✅ **If you see the login page, installation is successful!**

---

## ⚡ Phase 4: Test the Application (5 minutes)

### Step 6: Login to Your Application

1. **Open browser and go to:**
   ```
   http://156.232.88.156
   ```

2. **Try the test user (from development):**
   - Email: `admin@test.com`
   - Password: `TestPass123!`
   
   **OR use the superuser you just created:**
   - Email: (what you entered)
   - Password: (what you entered)

3. **You should see:**
   - Dashboard with statistics
   - Navigation menu
   - User profile dropdown
   - Activity feed

✅ **Application is live!**

---

## ⚡ Phase 5: Test Auto-Deployment (5 minutes)

### Step 7: Make a Test Change

**On your local machine (PowerShell):**

```powershell
cd "c:\programing\Realtime projects\COMS\COMS PROJECT IMPLEMENTATTION\COMS"

# Make a small change to test auto-deployment
# Let's update a comment in a file
Add-Content -Path "README.md" -Value "`n<!-- Test deployment $(Get-Date) -->"

# Commit and push
git add README.md
git commit -m "Test: Verify auto-deployment workflow"
git push origin main
```

### Step 8: Monitor Deployment

1. **Go to GitHub Actions:**
   - https://github.com/onyangowanga/COMS-Construction-Operations-Management-System-/actions

2. **You should see:**
   - A new workflow run starting
   - Status: 🟡 In Progress

3. **Click on the workflow** to see real-time logs:
   - ✅ Test job (runs tests)
   - ✅ Build job (builds Docker image)
   - ✅ Deploy job (deploys to VPS)

4. **Wait for completion** (3-5 minutes)
   - All jobs should show ✅ green checkmarks

5. **Verify deployment on VPS:**
   
   SSH to VPS:
   ```bash
   ssh root@156.232.88.156
   cd /root/coms
   docker-compose -f docker-compose.prod.yml logs --tail=20 web
   ```
   
   You should see recent deployment logs.

✅ **Auto-deployment is working!**

---

## ⚡ Phase 6: Secure Your Installation (Optional - 10 minutes)

### Step 9: Change Default Passwords (Recommended)

**Still in VPS SSH:**

```bash
# Update .env.production
cd /root/coms
nano .env.production
```

**Update these:**
- `POSTGRES_PASSWORD` - Change from `coms_pass` to something secure
- `SECRET_KEY` - Already auto-generated, verify it looks random
- `EMAIL_HOST_USER` - Your actual email
- `EMAIL_HOST_PASSWORD` - Your email app password

**Save:** Ctrl+X, Y, Enter

**Restart containers:**
```bash
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

### Step 10: Setup SSL (If you have a domain)

**Skip this if you don't have a domain name yet.**

If you have a domain pointing to 156.232.88.156:

```bash
# Install Certbot
apt-get install -y certbot

# Stop Nginx
docker-compose -f docker-compose.prod.yml stop nginx

# Get certificate (replace yourdomain.com)
certbot certonly --standalone -d yourdomain.com

# Copy certificates
mkdir -p /root/coms/nginx/ssl
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem /root/coms/nginx/ssl/cert.pem
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem /root/coms/nginx/ssl/key.pem

# Edit Nginx config
nano /root/coms/nginx/conf.d/coms.conf
# Uncomment the HTTPS server block (remove # from lines)

# Update .env.production
nano /root/coms/.env.production
# Change:
# SECURE_SSL_REDIRECT=True
# SESSION_COOKIE_SECURE=True
# CSRF_COOKIE_SECURE=True

# Restart
docker-compose -f docker-compose.prod.yml up -d
```

---

## ✅ Deployment Complete!

### What You've Accomplished:

✅ VPS configured with Docker and Docker Compose
✅ COMS application deployed and running
✅ Nginx serving your application
✅ PostgreSQL database setup with migrations
✅ Redis caching enabled
✅ GitHub Actions CI/CD configured
✅ Auto-deployment on push to master branch
✅ Firewall configured and secured

### Your Application is Live At:

**URL:** http://156.232.88.156

**Test Login:**
- Email: `admin@test.com`
- Password: `TestPass123!`

**Or Your Superuser:**
- Email: (what you created)
- Password: (what you created)

---

## 📊 Daily Workflow

From now on, deploying updates is simple:

```powershell
# 1. Make your changes
# 2. Commit and push
git add .
git commit -m "Add new feature"
git push origin main

# 3. GitHub Actions automatically:
#    - Runs tests
#    - Builds images  
#    - Deploys to VPS
#    - Verifies deployment

# 4. Check deployment status on GitHub Actions tab
# 5. Your changes are live in ~5 minutes!
```

---

## 🆘 Quick Troubleshooting

### Application Not Loading?

```bash
# SSH to VPS
ssh root@156.232.88.156

# Check containers
docker ps

# Check logs
cd /root/coms
docker-compose -f docker-compose.prod.yml logs -f web

# Restart if needed
docker-compose -f docker-compose.prod.yml restart
```

### Deployment Failed on GitHub?

1. Go to Actions tab
2. Click failed workflow
3. Read error message
4. Common fixes:
   - Check VPS is online
   - Verify GitHub Secrets are correct
   - SSH to VPS and run `./deploy.sh` manually

### Need to Rollback?

```bash
# SSH to VPS
ssh root@156.232.88.156
cd /root/coms

# Check commit history
git log --oneline

# Rollback to previous commit
git checkout <previous-commit-hash>
./deploy.sh

# Or go back to latest
git checkout main
./deploy.sh
```

---

## 📚 Documentation References

- **Complete Guide:** `docs/VPS_DEPLOYMENT_GUIDE.md`
- **Quick Start:** `docs/QUICK_START_DEPLOYMENT.md`
- **Summary:** `docs/DEPLOYMENT_SUMMARY.md`
- **Frontend:** `docs/FRONTEND_IMPLEMENTATION.md`
- **Demo Guide:** `docs/CLIENT_DEMO_GUIDE.md`

---

## 🎉 Next Steps

1. **Configure Email:**
   - Update `.env.production` with SMTP settings
   - Test password reset emails

2. **Customize Branding:**
   - Update logo in templates
   - Change color scheme in CSS
   - Update company name

3. **Add Real Data:**
   - Create projects
   - Add team members
   - Upload documents

4. **Setup Monitoring:**
   - Configure error tracking
   - Setup uptime monitoring
   - Enable email notifications

5. **Plan SSL:**
   - Get domain name
   - Configure DNS
   - Install SSL certificate

---

**🚀 Your COMS application is now live and automatically deploying!**

**Need help?** Check the documentation or review error logs on VPS.

**Happy deploying!** 🎊
