# BrewStock Backend

FastAPI backend untuk Demand Forecast.

## Core
- Repository Pattern
- Strategy Pattern
- Observer Pattern
- Factory Pattern
- Redis forecast cache 3600s
- Sliding window rate limit
- JWT + refresh rotation

## Run
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
uvicorn src.app.main:app --reload
```

## Test
```bash
cd backend
pytest
```
