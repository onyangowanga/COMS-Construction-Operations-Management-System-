# 🚀 Direct Local-to-VPS Deployment Guide

Bypass GitHub Actions and deploy directly from your local machine to your VPS.

---

## ⚠️ IMPORTANT: Test Locally First!

**Before deploying to VPS, you MUST test your application locally using Docker.**

👉 **See [LOCAL_TESTING_GUIDE.md](LOCAL_TESTING_GUIDE.md) for complete step-by-step local testing instructions.**

### Quick Local Test Checklist:
```powershell
# 1. Start local containers
docker-compose up -d

# 2. Run migrations
docker-compose exec web python manage.py migrate

# 3. Create superuser
docker-compose exec web python manage.py createsuperuser

# 4. Test application
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000/admin

# 5. Run tests
docker-compose exec web pytest

# 6. ✅ If everything works, proceed with VPS deployment below
```

---

## ⚡ Quick Start (After Successful Local Testing)

### On Windows (PowerShell)
```powershell
cd "C:\programing\Realtime projects\COMS\COMS PROJECT IMPLEMENTATTION\COMS"
.\deploy-local-to-vps.ps1
```

### On Linux/Mac (Bash)
```bash
cd COMS
chmod +x deploy-local-to-vps.sh
./deploy-local-to-vps.sh
```

## 📋 Prerequisites

### 1. SSH Access to VPS
You need SSH access configured to your VPS.

#### First Time Setup - Password Authentication
The script will prompt for your VPS password each time.

#### Recommended - SSH Key Authentication
Set up SSH keys for passwordless deployment:

**Windows:**
```powershell
# Generate SSH key (if you don't have one)
ssh-keygen -t ed25519 -C "your-email@example.com"

# Copy public key to VPS
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh root@156.232.88.156 "cat >> ~/.ssh/authorized_keys"
```

**Linux/Mac:**
```bash
# Generate SSH key (if you don't have one)
ssh-keygen -t ed25519 -C "your-email@example.com"

# Copy public key to VPS
ssh-copy-id root@156.232.88.156
```

### 2. VPS Requirements
Your VPS should already have:
- Docker installed
- Docker Compose installed
- Git installed
- Project directory at `/root/coms`
- `.env.production` file configured

## 🎯 What the Script Does

1. **Tests SSH Connection** - Verifies you can connect to the VPS
2. **Creates Archive** - Packages your local code (excluding unnecessary files)
3. **Transfers Files** - Uploads archive to VPS via SCP
4. **Backs Up Current Deployment** - Creates backup of database and config
5. **Extracts New Code** - Unpacks archive on VPS
6. **Runs Deployment** - Executes the standard `deploy.sh` script
7. **Verifies Deployment** - Checks container status and health

## 📁 Files Excluded from Deployment

The following are automatically excluded:
- `.git` and `.github` directories
- `.env` files (uses existing `.env.production` on VPS)
- Virtual environments (`.venv`, `node_modules`)
- Python cache (`__pycache__`, `*.pyc`)
- Build artifacts (`dist`, `build`, `.next`)
- Static files (`staticfiles`, `media`) - regenerated on VPS
- Logs and temporary files
- IDE configurations (`.idea`, `.vscode`)

## 🔄 Deployment Workflow

### Typical Usage
```bash
# 1. Make your code changes locally
# 2. Test locally with Docker
docker-compose up

# 3. Deploy to VPS
.\deploy-local-to-vps.ps1

# 4. Verify deployment
# Visit: http://156.232.88.156
```

### Example Output
```
================================
COMS Direct VPS Deployment
Deploying from Local to VPS
================================

[INFO] Testing SSH connection to VPS...
[INFO] SSH connection successful!
[INFO] Creating deployment archive...
[INFO] Archive created: coms-deployment-20260323_143022.zip (15.4 MB)
[STEP] Transferring files to VPS...
[INFO] Upload complete!
[STEP] Executing deployment on VPS...
[VPS] Creating backup of current deployment...
[VPS] Backing up database...
[VPS] Extracting new deployment files...
[VPS] Running deployment script...
[INFO] Building Docker images...
[INFO] Starting containers...
[INFO] Running database migrations...
[VPS] Deployment completed!

================================
✅ Deployment Complete!
================================

Application URL: http://156.232.88.156
```

## 🔧 Troubleshooting

### SSH Connection Failed
**Error:** "Cannot connect to VPS"

**Solution:**
```bash
# Test SSH manually
ssh root@156.232.88.156

# If using password, you'll be prompted
# If using SSH key, make sure it's added to ssh-agent
```

### Permission Denied (Windows)
**Error:** "Cannot be loaded because running scripts is disabled"

**Solution:**
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try again
.\deploy-local-to-vps.ps1
```

### Deployment Failed on VPS
**Error:** Deployment script fails on VPS

**Solution:**
```bash
# SSH into VPS
ssh root@156.232.88.156

# Check logs
cd /root/coms
docker-compose -f docker-compose.prod.yml logs

# Try manual deployment
./deploy.sh
```

### Archive Too Large
**Issue:** Upload takes too long

**Workaround:**
The script already excludes unnecessary files, but if your media/static files are large, you can:
1. Manually clean up media files on VPS
2. Use rsync instead (more efficient for incremental updates)

## 🆚 Comparison: Direct vs GitHub Actions

| Feature | Direct Deployment | GitHub Actions |
|---------|------------------|----------------|
| **Cost** | Free (no GitHub quota) | Uses GitHub Actions minutes |
| **Speed** | Faster (no CI tests) | Slower (runs tests first) |
| **Testing** | Manual local testing | Automated CI tests |
| **Flexibility** | Deploy anytime | Only on git push |
| **Network** | Requires good upload speed | GitHub handles transfer |
| **Rollback** | Manual | Via git revert |

## 💡 Best Practices

### 1. Test Locally First
```bash
# Always test with local Docker before deploying
docker-compose up
```

### 2. Keep .env.production Updated
Make sure your VPS has the latest environment variables:
```bash
ssh root@156.232.88.156
cd /root/coms
nano .env.production
```

### 3. Monitor Deployment
Watch logs during deployment:
```bash
ssh root@156.232.88.156
cd /root/coms
docker-compose -f docker-compose.prod.yml logs -f
```

### 4. Create Database Backups
Before major deployments:
```bash
ssh root@156.232.88.156
cd /root/coms
docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U coms_user coms_db > backup_$(date +%Y%m%d).sql
```

## 🔄 Rollback Procedure

If deployment fails and you need to rollback:

```bash
# SSH into VPS
ssh root@156.232.88.156

# Find backup
ls -lt /root/coms-backups/

# Restore database
cd /root/coms
docker-compose -f docker-compose.prod.yml exec -T db psql -U coms_user coms_db < /root/coms-backups/deployment-YYYYMMDD_HHMMSS/database_backup.sql

# Or restore entire deployment
cd /root
rm -rf coms
git clone https://github.com/onyangowanga/COMS-Construction-Operations-Management-System-.git coms
cd coms
cp /root/coms-backups/deployment-YYYYMMDD_HHMMSS/.env.production .
./deploy.sh
```

## 🔐 Security Notes

1. **SSH Keys**: Use SSH keys instead of passwords for security
2. **VPS Access**: Keep your VPS credentials secure
3. **Environment Variables**: Never commit `.env.production` to git
4. **Backups**: Regular backups are created automatically before deployment

## 📞 Support

**VPS Details:**
- IP: 156.232.88.156
- User: root
- Project Path: /root/coms

**Application URLs:**
- Frontend: http://156.232.88.156
- Admin: http://156.232.88.156/admin
- API: http://156.232.88.156/api

**Manual Deployment:**
```bash
ssh root@156.232.88.156
cd /root/coms
./deploy.sh
```

---

**Quick Command Reference:**

```powershell
# Deploy to VPS
.\deploy-local-to-vps.ps1

# View VPS logs
ssh root@156.232.88.156 "cd /root/coms && docker-compose -f docker-compose.prod.yml logs -f"

# Check VPS status
ssh root@156.232.88.156 "cd /root/coms && docker ps --filter 'name=coms'"

# Restart VPS services
ssh root@156.232.88.156 "cd /root/coms && docker-compose -f docker-compose.prod.yml restart"
```
