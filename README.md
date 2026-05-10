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

## Quick Start (Menjalankan Aplikasi)

Jalankan perintah di bawah ini dari direktori root repository (`BrewStock/`).

### 🍎 macOS / Linux / Git Bash (1 Row)

```bash
(cd backend && source .venv/bin/activate && uvicorn src.app.main:app --rel
oad --port 8000) & (cd frontend && npm run dev -- --host 0.0.0.0 --port 5173)
```

---

### ⚡ Windows (PowerShell — 1 command Otomatis open Window)

Perintah ini akan membuka 2 jendela PowerShell baru untuk menjalankan backend dan frontend secara bersamaan:

```powershell
Start-Process powershell -ArgumentList "-NoExit -Command `"cd backend; python -m venv .venv; .venv\Scripts\Activate.ps1; pip install -e '.[dev]'; if (-not (Test-Path .env)) { Copy-Item .env.example .env }; uvicorn src.app.main:app --reload --port 8000`""; Start-Process powershell -ArgumentList "-NoExit -Command `"cd frontend; npm install; npm run dev -- --host 0.0.0.0 --port 5173`"""
```

---

### 💻 Windows (Command Prompt / CMD — 1 row)

```cmd
start cmd /k "cd backend && python -m venv .venv && call .venv\Scripts\activate.bat && pip install -e .[dev] && (if not exist .env copy .env.example .env) && uvicorn src.app.main:app --reload --port 8000" && start cmd /k "cd frontend && npm install && npm run dev -- --host 0.0.0.0 --port 5173"
```

---

### 🛠️ Cara Manual (2 Terminal pisah)

Jika Anda ingin menjalankan dan memantau proses secara manual di dua tab/terminal terpisah:

#### 1. Terminal Backend
* **macOS / Linux / Git Bash:**
  ```bash
  cd backend
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -e ".[dev]"
  cp -n .env.example .env
  uvicorn src.app.main:app --reload --port 8000
  ```
* **Windows (PowerShell):**
  ```powershell
  cd backend
  python -m venv .venv
  .venv\Scripts\Activate.ps1
  pip install -e ".[dev]"
  if (-not (Test-Path .env)) { Copy-Item .env.example .env }
  uvicorn src.app.main:app --reload --port 8000
  ```

#### 2. Terminal Frontend (Semua OS)
```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

> **Catatan Penting:**
> - Backend berjalan di `http://localhost:8000`, frontend di `http://localhost:5173`.
> - Edit `backend/.env` untuk mengatur koneksi database, Redis, dan JWT secret sebelum production.
> - **Menghentikan Proses:** 
>   - Pada macOS/Linux (jika memakai satu baris): Tekan `Ctrl+C` atau jalankan `kill %1 %2`.
>   - Pada Windows (jika memakai perintah satu baris di atas): Cukup tutup kedua jendela terminal baru yang terbuka.

## Endpoint utama
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/inventory/summary`
- `GET /api/v1/inventory/transactions`
- `POST /api/v1/inventory/transactions`
- `DELETE /api/v1/inventory/transactions/{transactionId}`
- `POST /api/v1/forecast/demand`