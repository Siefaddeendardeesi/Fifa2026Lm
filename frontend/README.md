# FIFA2026LM Frontend

Production Next.js frontend for the FIFA World Cup 2026 ML prediction platform.

## Stack

- Next.js 16 (App Router)
- React 19 + TypeScript
- Tailwind CSS v4 + shadcn/ui
- TanStack Query (React Query)
- Axios
- Framer Motion

## Getting Started

1. Ensure the FastAPI backend is running at `http://localhost:8000`
2. Install dependencies:

```bash
npm install
```

3. (Optional) Configure API URL:

```bash
cp .env.local.example .env.local
```

4. Start the dev server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Docker

From the `docker/` directory (requires `docker/.env` — copy from `.env.example`):

```bash
docker compose up --build
```

| Service  | URL                     |
|----------|-------------------------|
| Frontend | http://localhost:3000   |
| Backend  | http://localhost:8000   |
| MLflow   | http://localhost:5000   |
| Grafana  | http://localhost:3001   |

The frontend image is built with `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`) so browser-side API calls reach the exposed backend port. Inside the Docker network the backend is reachable at `http://backend:8000` via the `api` service alias.

```bash
# Build frontend image only
docker build -t fifa2026-frontend ./frontend
```

## Pages

| Route | Description |
|-------|-------------|
| `/` | Home — top teams, champion preview, navigation |
| `/groups` | 12 group stage draw (A–L) |
| `/teams` | All 48 nations |
| `/rankings` | ELO, model, hybrid rankings (sortable) |
| `/predictions` | Head-to-head match predictor |
| `/simulation` | Monte Carlo tournament simulation |

## Project Structure

```
src/
  app/           # Next.js App Router pages
  components/    # UI components
  lib/
    api/         # Axios API client & endpoints
    hooks/       # React Query hooks
    types/       # TypeScript interfaces
    constants/   # Team flags, helpers
```
