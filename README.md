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
- Backend demand forecast selesai
- Auth JWT + refresh rotation siap
- Sliding window rate limit siap
- Unit test backend: pass
- Frontend scaffold: Vite + React + TypeScript (siap dijalankan)

## Quick start (macOS — satu baris dari root repo)

```bash
(cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -e .[dev] && cp -n .env.example .env && .venv/bin/uvicorn src.app.main:app --reload --port 8000) & (cd frontend && npm install && npm run dev)
```

> **Catatan:**
> - Jalankan dari direktori root repo (`BrewStock/`).
> - Backend berjalan di `http://localhost:8000`, frontend di `http://localhost:5173`.
> - Edit `backend/.env` untuk mengatur koneksi database, Redis, dan JWT secret sebelum production.
> - Untuk menghentikan semua proses: tekan `Ctrl+C` dua kali atau jalankan `kill %1 %2`.
