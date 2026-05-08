# PRD BrewStock — AI Inventory Assistant for Coffee Shop

**Version:** 1.0 | **Deadline:** 24 Mei 2026 | **Course:** II4012 ITB STI

## 1. Overview
BrewStock adalah platform manajemen inventaris berbasis AI untuk coffee shop skala UMKM. Tiga masalah utama yang diselesaikan:
- Pencatatan stok manual yang error-prone
- Ketidakmampuan prediksi demand seasonal
- Kesulitan menginterpretasi data mentah menjadi aksi operasional.

Tiga komponen AI sesuai spesifikasi Tubes:
| Komponen | Kategori Tubes | Teknologi |
| --- | --- | --- |
| Demand Forecast | ML Custom (latih sendiri) | Prophet / XGBoost |
| Stock Image Scanner | AI Bebas | YOLOv8 / MobileNet |
| Insight Generator | AIaaS | Claude / GPT API |

## 2. KPI Sukses
Dari spesifikasi dokumen:
- MAPE prediksi bahan baku < 5%
- F1-Score YOLO > 0.85
- Pembusukan bahan < 7% per bulan
- Transaksi batal karena stockout < 2 kasus/bulan
- Pengecekan manual < 15 menit/hari.

## 3. System Architecture
```
┌─────────────────────────────────────────┐
│           BrewStock Frontend            │
│   React + TypeScript (Vite)             │
│   Lighthouse Accessibility + CLS/LCP    │
└────────────┬───────────────┬────────────┘
             │               │
    ┌────────▼───┐    ┌──────▼──────┐
    │ API Gateway│    │  CDN Layer  │
    │ Rate Limit │    │ Cloudflare  │
    │ (Sliding   │    │ (static     │
    │  Window)   │    │  assets)    │
    └────────┬───┘    └─────────────┘
             │
    ┌────────▼──────────────────────────┐
    │        FastAPI Backend            │
    │  ┌──────────┐  ┌───────────────┐  │
    │  │ Forecast │  │ Stock Scanner│  │
    │  │ Service  │  │ Service      │ │
    │  │(Prophet/XGBoost)│(YOLOv8)     │ 										 	 	 	 	 	 	 	 	 	 	 	 	 	 	 	 	 	 	|
their respective features and technologies.
detailing the architecture, security measures, and deployment strategies.
detailed steps for development phases, including data understanding, modeling, evaluation, deployment,
and frontend features.

