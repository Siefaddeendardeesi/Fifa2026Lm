# Railway Full Stack Deployment Guide

This guide deploys your FIFA 2026 ML platform as a full stack on Railway with frontend, backend, and database.

## Prerequisites

1. **Railway Account**: Sign up at https://railway.app
2. **GitHub Repository**: Push your code to GitHub (Railway integrates with GitHub)
3. **Docker**: Installed locally for building and testing
4. **Railway CLI**: Install with `npm install -g @railway/cli`

## Deployment Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Railway Project                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │  Frontend    │  │   Backend    │  │ PostgreSQL│ │
│  │  (Next.js)   │─→│   (FastAPI)  │─→│  (DB)     │ │
│  │  Port: 3000  │  │  Port: 8000  │  │           │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
│       ↓                   ↓                          │
│   Railway Domain      Railway Domain                 │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Step 1: Prepare Your Code

### Create `.railwayignore` (optional)
```
notebooks/
.mypy_cache/
.pytest_cache/
.ruff_cache/
htmlcov/
mlruns/
__pycache__/
*.pyc
.env
```

### Update Frontend Build Configuration

Ensure `frontend/next.config.js` has proper output settings:
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
}

module.exports = nextConfig
```

## Step 2: Deploy Backend (FastAPI)

### Option A: Using Railway Dashboard

1. Go to https://railway.app/dashboard
2. Click **+ New Project**
3. Select **Deploy from GitHub repo**
4. Connect your GitHub repository
5. Select the repository
6. Create a new **Service** → choose **Docker**
7. Configure:
   - **Root Directory**: `.` (project root)
   - **Dockerfile**: `docker/Dockerfile`
   - **Port**: `8000`

### Option B: Using Railway CLI

```bash
# Login to Railway
railway login

# Create a new project
railway init

# Deploy backend
railway up

# Link to GitHub repo
railway link [repo-url]
```

### Backend Environment Variables

Set in Railway Dashboard → Service Settings → Variables:

```
ENVIRONMENT=production
POSTGRES_HOST=${{Postgres.RAILWAY_PRIVATE_URL}}
POSTGRES_PORT=5432
POSTGRES_USER=fifa2026
POSTGRES_PASSWORD=${{Postgres.RAILWAY_DB_PASSWORD}}
POSTGRES_DB=fifa2026
MLFLOW_TRACKING_URI=http://localhost:5000
```

## Step 3: Deploy Frontend (Next.js)

### In Railway Dashboard

1. **+ New Service** → **Docker**
2. Configure:
   - **Root Directory**: `frontend`
   - **Dockerfile**: `frontend/Dockerfile`
   - **Port**: `3000`

### Frontend Build Arguments & Variables

Set in Railway Dashboard → Service Settings:

**Build Arguments:**
```
NEXT_PUBLIC_API_URL=${{Backend.RAILWAY_PUBLIC_URL}}
```

**Environment Variables:**
```
NODE_ENV=production
NEXT_TELEMETRY_DISABLED=1
PORT=3000
HOSTNAME=0.0.0.0
```

## Step 4: Deploy Database

1. **+ New Service** → **Database** → **PostgreSQL**
2. Railway auto-generates:
   - `RAILWAY_PRIVATE_URL` (internal connection string)
   - Credentials for backend connection

## Step 5: Configure Service Networking

### Connect Frontend to Backend

In Frontend service variables, add:
```
NEXT_PUBLIC_API_URL=${{Backend.RAILWAY_PUBLIC_URL}}
```

This ensures the frontend browser client connects to the backend's public URL.

### Connect Backend to Database

Already configured via `POSTGRES_HOST=${{Postgres.RAILWAY_PRIVATE_URL}}`

## Step 6: Deploy via GitHub Push (Recommended)

Once configured, Railway auto-deploys on every push to your main branch:

```bash
git push origin main
```

Railway automatically:
- Builds Docker images
- Deploys services
- Restarts on failure
- Manages SSL/TLS certificates

## Step 7: Verify Deployment

### Check Service Status
```bash
railway status
```

### View Logs
```bash
# Backend logs
railway logs -s backend

# Frontend logs
railway logs -s frontend

# Database logs
railway logs -s postgres
```

### Test Endpoints
```bash
# Get service URLs
railway domains

# Test backend API
curl https://<backend-url>/health

# Test frontend
open https://<frontend-url>
```

## Environment Variables Reference

### Backend (FastAPI)
```
ENVIRONMENT=production
POSTGRES_HOST=postgres_service_url
POSTGRES_PORT=5432
POSTGRES_USER=fifa2026
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=fifa2026
MLFLOW_TRACKING_URI=http://localhost:5000  # or external MLflow
KAGGLE_USERNAME=
KAGGLE_KEY=
APIFY_TOKEN=
```

### Frontend (Next.js)
```
NEXT_PUBLIC_API_URL=https://backend-url  # Public backend URL
NODE_ENV=production
```

## Step 8: Post-Deployment

### Run Database Migrations
```bash
railway run --service backend -- python scripts/build_features.py
```

### Monitor & Scale
- Railway Dashboard → Service → Resources
- Adjust CPU and Memory as needed
- Set auto-scaling (optional)

### Custom Domain
- Railway Dashboard → Service → Domain
- Add custom domain or use Railway subdomain

### CI/CD Pipeline
Railway automatically deploys on:
- Push to `main` branch
- Merge to `main` via PR
- Manual redeploy button

## Troubleshooting

### Frontend Can't Reach Backend
- Verify `NEXT_PUBLIC_API_URL` is set to backend's public URL
- Check CORS settings in `app/api/main.py`
- Ensure backend service is running

### Database Connection Fails
- Verify `POSTGRES_HOST` is set to Railway's private URL
- Check database credentials match
- Test with `psql` from Railway console

### Build Fails
- Check `railway logs -s backend`
- Verify Dockerfile paths are correct
- Ensure all dependencies in `pyproject.toml`

### Slow Deploys
- First deploy takes 5-10 minutes (building dependencies)
- Subsequent deploys are faster (layer caching)
- Monitor with `railway status`

## Cost Estimation

Railway pricing (as of 2024):
- **Compute**: $0.50/GB RAM/hour
- **PostgreSQL**: $5/month per instance
- **Bandwidth**: Included
- **Example cost**: ~$30-50/month for small production instance

## Local Testing Before Deploy

### Test with Docker Compose
```bash
docker compose -f docker/docker-compose.yml up
```

### Test Frontend Build
```bash
cd frontend
npm run build
npm start
```

### Test Backend
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -e ".[dev]"
uvicorn app.api.main:app --reload
```

## Next Steps

1. ✅ Deploy backend service
2. ✅ Deploy frontend service
3. ✅ Deploy PostgreSQL database
4. ⏭️ Add monitoring (Datadog, Sentry)
5. ⏭️ Set up CI/CD notifications
6. ⏭️ Configure backups
7. ⏭️ Add custom domain & SSL
8. ⏭️ Set up environment-specific configs (staging, production)

## Quick Deploy Command

```bash
# One-liner after Railway project setup
railway up --service backend && railway up --service frontend
```

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://railway.app/discord
- Your API Docs: `https://<backend-url>/docs`
- Dashboard: `https://railway.app/dashboard`
