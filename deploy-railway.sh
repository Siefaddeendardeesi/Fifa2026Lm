#!/usr/bin/env bash
# Deploy FIFA 2026 Full Stack to Railway
# Usage: ./deploy-railway.sh

set -euo pipefail

echo "🚀 FIFA 2026 Full Stack Deployment to Railway"
echo "=============================================="

# Check prerequisites
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Install with: npm install -g @railway/cli"
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo "❌ Git not found. Please install Git."
    exit 1
fi

# Initialize Railway project if not exists
if [ ! -f "railway.json" ]; then
    echo "📦 Initializing Railway project..."
    railway init --create-new --name fifa2026lm
fi

echo ""
echo "📝 Step 1: Ensure code is committed to Git"
git status
echo ""
read -p "Proceed with deployment? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

echo ""
echo "🔌 Step 2: Connecting to Railway..."
railway login

echo ""
echo "🏗️  Step 3: Deploying Backend (FastAPI)"
railway up --service backend

echo ""
echo "🎨 Step 4: Deploying Frontend (Next.js)"
railway up --service frontend

echo ""
echo "🗄️  Step 5: Deploying PostgreSQL Database"
railway add --plugin postgres

echo ""
echo "✅ Deployment Complete!"
echo ""
echo "View your services:"
railway status

echo ""
echo "Get service URLs:"
railway domains

echo ""
echo "View logs:"
echo "  Backend:  railway logs -s backend"
echo "  Frontend: railway logs -s frontend"
echo "  Database: railway logs -s postgres"

echo ""
echo "📖 For detailed instructions, see RAILWAY_DEPLOYMENT.md"
