# 🚀 Quick Deploy to Railway - Full Stack (Frontend + Backend)

## 5-Minute Quick Start

### Step 1: Prepare (1 min)
```bash
# Ensure code is on GitHub
git remote -v
git push origin main

# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login
```

### Step 2: Deploy Backend (2 min)
```bash
# Create Railway project
railway init

# Deploy backend
railway up

# Note the Railway URL (e.g., backend-service.railway.app)
# You'll need this for the frontend
```

### Step 3: Deploy Frontend (1 min)
```bash
# Add frontend service
railway add service

# Select Docker
# Set Dockerfile path to: frontend/Dockerfile

# Wait for build to complete
railway status
```

### Step 4: Add Database (1 min)
```bash
# Add PostgreSQL
railway add --plugin postgres

# This auto-creates connection environment for backend
```

### Step 5: Set Variables (0 min, automated)

Variables are auto-linked between services. Just set:

**Backend Service Variables:**
```
ENVIRONMENT=production
POSTGRES_USER=fifa2026
POSTGRES_PASSWORD=your-strong-password
POSTGRES_DB=fifa2026
```

**Frontend Service Variables:**
```
NEXT_PUBLIC_API_URL=https://your-backend-service.railway.app
NODE_ENV=production
```

---

## What Gets Deployed

| Service | URL | Purpose |
|---------|-----|---------|
| **Backend API** | `https://backend-service.railway.app` | FastAPI with ML predictions |
| **Frontend UI** | `https://frontend-service.railway.app` | Next.js React app |
| **Database** | Private Railway network | PostgreSQL data storage |

---

## Access Your App

```
🌐 Frontend:  https://frontend-service.railway.app
🔌 API Docs:  https://backend-service.railway.app/docs
📊 Health:    https://backend-service.railway.app/health
```

---

## View Logs

```bash
# Backend logs
railway logs -s backend

# Frontend logs  
railway logs -s frontend

# Database logs
railway logs -s postgres

# Real-time monitoring
railway status
```

---

## Troubleshooting

### Frontend shows 404 / can't find API
```bash
# Verify NEXT_PUBLIC_API_URL is set to your backend URL
railway set NEXT_PUBLIC_API_URL=https://your-backend.railway.app

# Redeploy frontend
railway redeploy -s frontend
```

### Backend can't connect to database
```bash
# Check database is running
railway status

# Verify POSTGRES_HOST is set to internal Railway URL
railway set POSTGRES_HOST=postgres.railway.internal
```

### Build is very slow
- First deploy: 5-10 minutes (builds dependencies)
- Subsequent: 1-3 minutes (cached layers)
- Monitor with: `railway status`

---

## Environment Variables Reference

### Backend
```env
ENVIRONMENT=production
POSTGRES_HOST=postgres.railway.internal  # or ${{Postgres.RAILWAY_PRIVATE_URL}}
POSTGRES_PORT=5432
POSTGRES_USER=fifa2026
POSTGRES_PASSWORD=strong-password
POSTGRES_DB=fifa2026
```

### Frontend
```env
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
NODE_ENV=production
PORT=3000
```

---

## Custom Domain (Optional)

1. Go to Railway Dashboard → Service → Domain
2. Add your domain (e.g., `api.yourdomain.com`)
3. Follow DNS setup instructions
4. Railway handles SSL automatically

---

## Rollback Deployment

```bash
# List previous deployments
railway logs --show-deployments

# Redeploy previous version
railway redeploy [version-id]
```

---

## Useful Commands

```bash
# Check service status
railway status

# View environment variables
railway variables

# Set environment variable
railway set KEY=value

# Remove environment variable  
railway unset KEY

# Connect to database (local terminal)
railway database:connect

# SSH into service container
railway shell -s backend

# Stop service
railway stop -s backend

# Delete service
railway remove -s frontend

# View cost/usage
railway billing
```

---

## Performance Tuning

### Scale Resources
Railway Dashboard → Service → Resources → Adjust CPU/Memory

**Recommended:**
- Backend: 512MB RAM, 0.5 CPU
- Frontend: 256MB RAM, 0.25 CPU
- Database: 512MB RAM

### Enable Auto-scaling
- Dashboard → Service → Advanced → Enable Auto Scaling
- Set min/max replicas

### Monitor Metrics
- Dashboard → Service → Analytics
- View response times, error rates, resource usage

---

## Next Steps

1. ✅ Deploy backend & frontend
2. ⏭️ Set up custom domain
3. ⏭️ Add monitoring (Sentry, Datadog)
4. ⏭️ Configure backups
5. ⏭️ Set up staging environment
6. ⏭️ Add GitHub branch auto-deploy

---

## Get Help

- Railway Docs: https://docs.railway.app
- Discord: https://railway.app/discord
- Status: https://status.railway.app
- Support: In Railway Dashboard → Help

---

**Your deployed app is now live!** 🎉

Monitor it at: https://railway.app/dashboard
