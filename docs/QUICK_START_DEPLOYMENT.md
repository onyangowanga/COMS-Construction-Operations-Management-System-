# 🚀 Quick Start - Deploy COMS to VPS

Get your COMS application running on your VPS in ~15 minutes!

---

## Step 1: Connect to VPS (2 minutes)

Open PowerShell/Terminal and run:

```bash
ssh root@156.232.88.156
# Password: Coms@0722!
```

---

## Step 2: Initial Setup (10 minutes)

Run this single command:

```bash
curl -o setup-vps.sh https://raw.githubusercontent.com/onyangowanga/COMS-Construction-Operations-Management-System-/master/setup-vps.sh && chmod +x setup-vps.sh && ./setup-vps.sh
```

**Follow the prompts:**
1. Review `.env.production` settings (press Ctrl+X, Y, Enter to save)
2. Create superuser account when prompted
3. Wait for containers to build and start

---

## Step 3: Configure GitHub Secrets (2 minutes)

1. Go to: https://github.com/onyangowanga/COMS-Construction-Operations-Management-System-/settings/secrets/actions

2. Add these three secrets:

| Name | Value |
|------|-------|
| `VPS_HOST` | `156.232.88.156` |
| `VPS_USERNAME` | `root` |
| `VPS_PASSWORD` | `Coms@0722!` |

---

## Step 4: Access Your Application (1 minute)

Open browser and visit:

```
http://156.232.88.156
```

**Login with:**
- Email: `admin@test.com`
- Password: `TestPass123!`

Or use the superuser credentials you created.

---

## ✅ You're Done!

### What happens next?

Whenever you push code to the `main` branch:
```bash
git add .
git commit -m "Update"
git push origin main
```

GitHub Actions will automatically:
1. Run tests ✅
2. Build Docker images 🐳
3. Deploy to VPS 🚀
4. Verify deployment ✓

---

## 🆘 Need Help?

**Application not loading?**
```bash
ssh root@156.232.88.156
cd /root/coms
docker-compose -f docker-compose.prod.yml logs -f
```

**Manual deployment:**
```bash
ssh root@156.232.88.156
cd /root/coms
./deploy.sh
```

**Full documentation:**
- See: `docs/VPS_DEPLOYMENT_GUIDE.md`

---

## 📊 Common Commands

```bash
# SSH to VPS
ssh root@156.232.88.156

# View logs
cd /root/coms
docker-compose -f docker-compose.prod.yml logs -f

# Restart containers
docker-compose -f docker-compose.prod.yml restart

# Manual deployment
./deploy.sh

# Create new superuser
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

---

**Your COMS application is now live and will auto-deploy on every push!** 🎉
