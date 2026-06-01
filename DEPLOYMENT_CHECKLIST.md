# Full Stack Deployment Checklist

## Pre-Deployment ✓

- [ ] Code is pushed to GitHub (`git push origin main`)
- [ ] All environment variables documented in `.env.example`
- [ ] Docker images build locally: `docker compose up`
- [ ] Tests pass: `pytest tests/`
- [ ] No hardcoded secrets in code (use environment variables)
- [ ] `frontend/next.config.js` has `output: 'standalone'`
- [ ] Backend `docker/Dockerfile` is optimized (multi-stage)
- [ ] Frontend `frontend/Dockerfile` is optimized (3-stage build)

## Railway Account Setup ✓

- [ ] Create account at https://railway.app
- [ ] Verify email
- [ ] Connect GitHub account
- [ ] Create new project

## CLI Setup ✓

- [ ] Install Railway CLI: `npm install -g @railway/cli`
- [ ] Login: `railway login`
- [ ] Verify: `railway status`

## Backend Deployment ✓

- [ ] Initialize Railway: `railway init`
- [ ] Deploy backend: `railway up`
- [ ] Verify build logs: `railway logs -s backend`
- [ ] Get backend URL: `railway domains`
- [ ] Test health endpoint: `curl https://backend-url/health`
- [ ] Set environment variables:
  - [ ] `ENVIRONMENT=production`
  - [ ] `POSTGRES_USER=fifa2026`
  - [ ] `POSTGRES_PASSWORD=<strong-password>`
  - [ ] `POSTGRES_DB=fifa2026`

## Frontend Deployment ✓

- [ ] Add frontend service: `railway add service`
- [ ] Select Docker build
- [ ] Set Dockerfile: `frontend/Dockerfile`
- [ ] Wait for build (5-10 min)
- [ ] Get frontend URL: `railway domains`
- [ ] Set environment variables:
  - [ ] `NEXT_PUBLIC_API_URL=https://backend-url`
  - [ ] `NODE_ENV=production`

## Database Setup ✓

- [ ] Add PostgreSQL: `railway add --plugin postgres`
- [ ] Verify connection: `railway database:connect`
- [ ] Run migrations (if needed):
  ```bash
  railway run -s backend -- python scripts/build_features.py
  ```
- [ ] Verify data: Query a table from Railway console

## Service Networking ✓

- [ ] Backend can reach database:
  ```bash
  railway logs -s backend | grep -i "database\|connected"
  ```
- [ ] Frontend can reach backend:
  ```bash
  # Test from browser console at frontend URL
  fetch('/api/health')
  ```
- [ ] Backend CORS allows frontend domain (if needed)

## Post-Deployment Verification ✓

- [ ] Frontend loads: Visit `https://frontend-url`
- [ ] API docs accessible: Visit `https://backend-url/docs`
- [ ] Health checks pass:
  ```bash
  curl https://backend-url/health
  ```
- [ ] Database connected:
  ```bash
  railway logs -s backend | grep "database"
  ```
- [ ] No error messages in logs:
  ```bash
  railway logs -s backend
  railway logs -s frontend
  ```

## Performance & Monitoring ✓

- [ ] Check resource usage:
  ```bash
  railway status
  ```
- [ ] Set up resource limits in Dashboard
  - [ ] Backend: 512MB RAM, 0.5 CPU
  - [ ] Frontend: 256MB RAM, 0.25 CPU
  - [ ] Database: 512MB RAM
- [ ] Enable metrics/monitoring in Dashboard
- [ ] Set up auto-restart for failed services

## Custom Domain (Optional) ✓

- [ ] Buy domain (e.g., `yourdomain.com`)
- [ ] In Railway Dashboard → Service → Domain
- [ ] Add custom domain
- [ ] Update DNS records (Railway provides instructions)
- [ ] Wait for SSL certificate (auto-generated)
- [ ] Test: `https://yourdomain.com`

## Security Checklist ✓

- [ ] No secrets in Git (use Railway variables)
- [ ] HTTPS enabled (Railway default)
- [ ] Environment: `production`
- [ ] Database password is strong (20+ chars, mixed case)
- [ ] CORS configured correctly (if needed)
- [ ] Backend validates all inputs
- [ ] Frontend doesn't expose sensitive data

## Documentation ✓

- [ ] Update README with deployed URLs
- [ ] Document environment variables
- [ ] Create runbook for common tasks:
  - [ ] How to scale services
  - [ ] How to view logs
  - [ ] How to redeploy
  - [ ] How to rollback

## Monitoring & Alerts (Optional) ✓

- [ ] Set up error tracking (Sentry, Datadog)
- [ ] Configure log aggregation
- [ ] Set up uptime monitoring
- [ ] Configure Slack/email alerts
- [ ] Monitor database size

## Backup & Disaster Recovery ✓

- [ ] Enable automated database backups (Railway)
- [ ] Document backup location
- [ ] Test restore procedure
- [ ] Document rollback steps

## Team Access ✓

- [ ] Invite team members to Railway project
- [ ] Set proper permissions
- [ ] Share deployment documentation
- [ ] Create deployment runbook

## Final Checklist ✓

- [ ] All services show `Up` status: `railway status`
- [ ] No critical errors in logs
- [ ] Frontend + Backend + Database all running
- [ ] URLs are working and accessible
- [ ] Performance is acceptable
- [ ] No data loss or inconsistencies
- [ ] Team can access and monitor

---

## Rollback Plan

If something goes wrong:

```bash
# View previous deployments
railway logs --show-deployments

# Redeploy previous version
railway redeploy [version-id]
```

Or via Dashboard: Service → Deployments → Select & Redeploy

---

## Support

- Stuck? Check: `QUICK_DEPLOY.md` and `RAILWAY_DEPLOYMENT.md`
- Error logs: `railway logs -s <service>`
- Railway Dashboard: https://railway.app/dashboard
- Railway Support: https://railway.app/discord

---

**Deployment Status: Ready to Go!** ✅
