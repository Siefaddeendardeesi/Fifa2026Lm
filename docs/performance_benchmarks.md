# Performance Benchmarks

Measured on Windows 10, Python 3.12, 48-team World Cup dataset (~50K feature rows).

| Operation | Typical Duration | Optimizations |
|-----------|-----------------|---------------|
| ETL download (GitHub fallbacks) | 30–60 s | Retry with backoff, file caching |
| Feature build (full) | 2–5 min | Vectorized form features, as-of joins |
| Model training (XGBoost, 200 trees) | 30–90 s | `n_jobs=-1` |
| Optuna tuning (30 trials) | 5–15 min | CV pruning, parallel folds |
| Single prediction (API) | < 50 ms | Pre-loaded pipeline |
| Simulation (500 runs, 48 teams) | 1–3 min | Probability cache, multiprocessing |
| Simulation (2000 runs) | 3–8 min | 4 workers default |
| Rankings (48-team pool) | 10–30 s | Cached snapshots |

## Optimization Techniques

- **Vectorization** — pandas rolling/groupby for form features
- **Caching** — `@st.cache_data` in dashboard; match probability cache in simulation
- **Multiprocessing** — `ProcessPoolExecutor` for simulations ≥ 10 × workers
- **ETL caching** — skip re-download when checksum unchanged
- **Parquet** — columnar storage for features

## API Latency Targets

| Endpoint | p95 Target |
|----------|-----------|
| /health | < 10 ms |
| /predict | < 100 ms |
| /rankings | < 500 ms |
| /simulate (500) | < 180 s |

Monitor via Prometheus histogram `fifa_prediction_latency_seconds` and Grafana dashboard.

## Scaling Recommendations

- **API**: increase `API_WORKERS` or deploy behind Nginx load balancer
- **Simulation**: increase `SIMULATION_WORKERS`; consider pre-computing probability cache
- **Training**: use MLflow remote tracking server; schedule via CI/CD or Airflow
