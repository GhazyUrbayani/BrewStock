# BrewStock

AI inventory system for coffee shop.

## Stack
- Frontend: React + TypeScript (Vite)
- Backend: FastAPI
- Data: PostgreSQL + Redis
- Forecast: Prophet, XGBoost
- Vision: YOLOv8
- AIaaS: Claude, GPT

## Structure
- `backend/` FastAPI service
- `frontend/` React + TypeScript (Vite) app
- `ml/` ML module scaffold
- `infra/` Infra scaffold

## Current status
- Backend auth + inventory + forecast sudah terhubung
- JWT + refresh rotation siap
- Sliding window rate limit siap
- Forecast cache Redis dengan fallback in-memory untuk mode dev
- Frontend dashboard operasional sudah terintegrasi ke API

## Quick start (macOS — satu baris dari root repo)

```bash
(cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -e .[dev] && cp -n .env.example .env && .venv/bin/uvicorn src.app.main:app --reload --port 8000) & (cd frontend && npm install && npm run dev -- --host 0.0.0.0 --port 5173)
```

> **Catatan:**
> - Jalankan dari direktori root repo (`BrewStock/`).
> - Backend berjalan di `http://localhost:8000`, frontend di `http://localhost:5173`.
> - Edit `backend/.env` untuk mengatur koneksi database, Redis, dan JWT secret sebelum production.
> - Untuk menghentikan semua proses: tekan `Ctrl+C` dua kali atau jalankan `kill %1 %2`.

## Endpoint utama
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/inventory/summary`
- `GET /api/v1/inventory/transactions`
- `POST /api/v1/inventory/transactions`
- `DELETE /api/v1/inventory/transactions/{transactionId}`
- `POST /api/v1/forecast/demand`
