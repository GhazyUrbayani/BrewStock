# BrewStock Backend

FastAPI backend untuk auth, inventory transactions, dan demand forecast.

## Core
- Repository pattern
- Strategy pattern (`prophet`, `xgboost`, dengan fallback baseline)
- Observer pattern (log + AI insight trigger)
- Factory pattern untuk AI provider
- JWT access token + refresh rotation
- Sliding window rate limit
- Forecast cache (Redis, otomatis fallback in-memory jika Redis belum aktif)

## API
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/inventory/summary`
- `GET /api/v1/inventory/transactions`
- `POST /api/v1/inventory/transactions`
- `DELETE /api/v1/inventory/transactions/{transactionId}`
- `POST /api/v1/forecast/demand`

## Run
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
uvicorn src.app.main:app --reload --port 8000
```

## Test
```bash
cd backend
source .venv/bin/activate
pytest -q
```
