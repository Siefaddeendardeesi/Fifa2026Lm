# FIFA World Cup 2026 Prediction Platform

Production-grade ML platform for FIFA World Cup 2026 match prediction, tournament simulation, and team rankings.

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -e ".[dev]"

cp .env.example .env
python scripts/download_data.py --skip-kaggle
python scripts/build_features.py
python scripts/train_baseline.py

streamlit run app/dashboard/main.py
uvicorn app.api.main:app --reload
```

## Docker

```bash
docker compose up --build
```

## Documentation

See [docs/](docs/) for architecture, API reference, deployment guide, and more.

## License

MIT
