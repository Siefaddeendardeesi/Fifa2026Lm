# API Reference

Base URL: `http://localhost:8000`

Interactive docs: `/docs` (Swagger) · `/redoc`

## Authentication

No authentication in default deployment. Rate limiting applies per IP.

## Endpoints

### GET /health

Health check.

**Response 200:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "model_loaded": true
}
```

### POST /predict

Predict match outcome probabilities.

**Request:**
```json
{
  "home_team": "Argentina",
  "away_team": "Brazil",
  "neutral": true
}
```

**Response 200:**
```json
{
  "home_team": "Argentina",
  "away_team": "Brazil",
  "home_win": 0.42,
  "draw": 0.28,
  "away_win": 0.30,
  "confidence": 0.42
}
```

**Errors:** 404 (team not found), 429 (rate limit)

### POST /simulate

Run Monte Carlo World Cup simulation.

**Request:**
```json
{
  "n_simulations": 500,
  "seed": 42
}
```

**Response 200:** champion/finalist/group-winner probability maps.

### GET /rankings

Query team rankings.

| Param | Default | Values |
|-------|---------|--------|
| method | model | elo, model, hybrid |
| since | 2024-01-01 | ISO date |
| pool_size | 48 | 2–48 |

### GET /teams

List all 48 World Cup teams with group and squad status.

### GET /groups

Return official 2026 group draw.

### GET /metrics

Prometheus metrics (text/plain).

## Error Format

```json
{
  "error": "No feature data for team: X",
  "details": {}
}
```

## Rate Limits

Default: 100 requests/minute per IP. Simulation: 10/minute.

Configured via `API_RATE_LIMIT` environment variable.
