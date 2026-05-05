# BrewStock Frontend

React + TypeScript (Vite) untuk dashboard operasional BrewStock.

## Fitur
- Login/register terhubung ke FastAPI
- Auto refresh access token via refresh token
- Input, list, filter, dan hapus demand transactions
- Ringkasan inventory per SKU
- Forecast panel (`prophet` atau `xgboost`) dengan chart dan sinyal restock
- Health indicator backend

## Konfigurasi
Secara default, frontend memanggil backend via Vite proxy (`/api` -> `http://localhost:8000`).

Opsional:
```bash
VITE_API_BASE_URL=http://localhost:8000
```

## Jalankan
```bash
cd frontend
npm install
npm run dev
```
