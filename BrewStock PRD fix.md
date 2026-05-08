# BrewStock — Product Requirements Document

> **Version:** 2.0  
> **Last Updated:** Mei 2026  
> **Course:** II4012 Inteligensi Artifisial untuk Bisnis, STI ITB

---

## 1. Latar Belakang & Problem Statement

Coffee shop skala UMKM di Indonesia tumbuh lebih dari 3.000 gerai per tahun, namun sekitar 60% masih mengelola stok secara manual. Akibatnya, dua masalah berlawanan muncul bersamaan: bahan baku expired karena overstock, dan pesanan batal karena kehabisan stok. Kedua kondisi ini secara langsung menggerus margin — estimasi kerugian inventory waste berkisar 15–20% dari modal bahan, sementara lost sales akibat stockout bisa mencapai 25% dari potensi pendapatan.

BrewStock hadir sebagai sistem manajemen inventaris berbasis AI yang menyerang tiga akar masalah sekaligus:

| Pain Point | Akar Masalah | Solusi AI |
|---|---|---|
| Catat stok manual | Human error + data latency tinggi | YOLO/MobileNet — hitung stok via foto |
| Tidak bisa prediksi demand | Tidak ada analisis pola historis | Prophet/XGBoost — time series forecast |
| Data teknis sulit diinterpretasi | Tidak ada layer insight yang mudah dibaca | Claude API — natural language insight |

**Problem Statement:** Bagaimana membangun sistem manajemen inventaris cerdas yang mampu mendigitalisasi stok fisik secara instan, memprediksi kebutuhan bahan baku secara akurat, dan memberikan rekomendasi operasional via interaksi bahasa alami — sehingga meningkatkan margin profit kedai kopi UMKM?

---

## 2. Target Pengguna

- **Owner / Manager** — melihat prediksi dan alert stok, membuat keputusan pembelian
- **Barista** — mengecek ketersediaan bahan sebelum membuat menu
- **Supervisor** — memantau KPI operasional harian

Ketiga role ini tidak selalu punya background teknikal. Semua output sistem harus bisa dibaca tanpa perlu memahami cara kerja model ML di baliknya.

---

## 3. KPI & Business Target

KPI ini bukan sekadar metrik teknikal — setiap angka punya alasan bisnis yang konkret.

| KPI | Target | Justifikasi Bisnis |
|---|---|---|
| Inventory waste (bahan expired) | < 7% per bulan | Di atas 7%, margin operasional mulai tergerus signifikan |
| Transaksi batal karena stockout | < 2 kasus per bulan | Setiap penolakan pesanan = kehilangan pelanggan potensial |
| Keberhasilan auto-restock | > 80% akurasi | Tanpa ini, sistem masih butuh intervensi manual tinggi |
| Pengecekan stok manual | < 15 menit per hari | Menghemat ~1 jam kerja barista per shift |
| MAPE prediksi demand | < 5% | Threshold industri untuk forecast yang actionable |
| F1-Score YOLO | > 0.85 | Precision-recall balance agar tidak banyak false alert |

### Indikator UX untuk Dashboard

Setiap KPI card di dashboard harus menampilkan tiga hal: angka saat ini, perubahan vs periode sebelumnya (naik/turun berapa persen), dan status terhadap target. Contoh:

```
Total Demand Minggu Ini: 1.240 unit
↑ 12% vs minggu lalu  |  Target: >1.000 unit  ✅
```

Tanpa konteks seperti ini, angka tidak bermakna bagi manager yang tidak tahu apakah 1.240 itu bagus atau buruk.

---

## 4. Komponen AI (Sesuai Spesifikasi Tubes)

### 4.1 ML Custom — Demand Forecast (Prophet + XGBoost)

Model time-series yang dilatih sendiri menggunakan data transaksi harian. Pipeline:

```
Raw POS Data
  → aggregate harian (groupby date + skuId)
  → feature engineering:
      dayOfWeek (0–6)
      isWeekend (bool)
      isHoliday (kalender Indonesia)
      weatherCategory (API / sintetis)
      lag_1, lag_7, lag_14
      rollingMean7
  → split train/val/test (time-based, BUKAN random)
  → train: Prophet (baseline) + XGBoost (challenger)
  → evaluate: MAPE, RMSE, walk-forward cross-validation
  → export: model.pkl → FastAPI service
```

Alasan pemilihan Prophet: handles seasonality weekly + yearly secara otomatis, bisa inject custom holiday (Lebaran, Natal, tanggal merah Indonesia), dan outputnya berupa confidence interval yang bisa langsung ditampilkan ke user sebagai "range prediksi."

Alasan XGBoost sebagai challenger: lebih baik capture nonlinear relationships antar fitur (misalnya interaksi cuaca × hari libur), dan feature importance-nya bisa dipakai untuk laporan analisis.

### 4.2 AIaaS — Insight Generator (Claude API)

Menerjemahkan angka forecast + kondisi stok menjadi rekomendasi bahasa Indonesia yang bisa dibaca siapa saja. Bukan chatbot general — context yang dikirim ke Claude berisi data aktual sistem:

```python
promptValue = f"""
Kamu adalah asisten manajer kedai kopi. Berdasarkan data berikut:
- SKU: {skuName}
- Stok saat ini: {currentStock} unit
- Prediksi demand 7 hari: {forecastTotal} unit
- Rekomendasi restock: {recommendedRestock} unit

Berikan satu paragraf rekomendasi operasional yang jelas dan praktis.
Jangan gunakan jargon teknikal.
"""
```

Fallback: jika API key tidak tersedia, sistem menggunakan `noopAiService` yang mengembalikan pesan default — sistem tidak crash.

### 4.3 AI Bebas — Stock Image Scanner (YOLOv8)

Object detection untuk menghitung stok fisik via foto, menggantikan hitungan manual. Base model: YOLOv8n pretrained COCO, di-fine-tune pada dataset gambar bahan kopi (susu, sirup, biji kopi, dll).

Target F1-Score > 0.85. Jika tidak tercapai dengan dataset minimal, gunakan data augmentation (flip horizontal, random brightness, Mosaic augmentation dari Ultralytics).

---

## 5. Arsitektur Sistem

```
┌─────────────────────────────────────────────────────┐
│                 BrewStock Frontend                  │
│         React + TypeScript (Vite)                   │
│   Lighthouse score: Accessibility > 90              │
│   CLS < 0.1  |  LCP < 2.5s                         │
└──────────────────────┬──────────────────────────────┘
                       │ HTTPS only
              ┌────────▼─────────┐
              │   Cloudflare     │
              │  CDN + WAF       │
              │  DDoS protection │
              └────────┬─────────┘
                       │
              ┌────────▼─────────────────────────────┐
              │          API Gateway                 │
              │   Rate Limit: Sliding Window         │
              │   100 req/min per IP                 │
              │   JWT validation                     │
              └────────┬─────────────────────────────┘
                       │
       ┌───────────────┼────────────────┐
       │               │                │
┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
│  Forecast   │ │   Scanner   │ │   Insight   │
│  Service   │ │   Service   │ │   Service   │
│ Prophet /  │ │  YOLOv8     │ │  Claude API │
│ XGBoost    │ └─────────────┘ └─────────────┘
└──────┬──────┘
       │
┌──────▼──────────────────────┐
│  PostgreSQL + Redis Cache   │
│  Index: (transactionDate,   │
│           skuId) composite  │
│  Redis TTL: 3600s           │
└─────────────────────────────┘
```

### Keputusan Arsitektur

**Kenapa service terpisah (bukan monolith)?**  
Setiap komponen AI punya karakteristik resource yang berbeda. Forecast service berat di CPU (model inference), Scanner service berat di memory (YOLO), Insight service berat di network I/O (external API). Dengan pemisahan, setiap service bisa di-scale secara independen tanpa menaikkan resource untuk seluruh sistem.

**Kenapa Redis cache?**  
Tanpa cache, setiap request forecast akan re-run Prophet yang butuh 3–8 detik. Cache dengan TTL 1 jam memotong response time ke < 100ms untuk request berulang di hari yang sama.

**Kenapa composite index `(transactionDate, skuId)`?**  
Query paling sering adalah "ambil transaksi SKU X dari tanggal Y sampai Z." Tanpa index ini, PostgreSQL harus full table scan — makin besar data, makin lambat. Dengan composite index, query yang sama turun dari O(n) ke O(log n).

---

## 6. Security

**Web Application Firewall (WAF)**  
Cloudflare WAF sebagai layer pertama. Block pattern: SQL injection, XSS, path traversal, command injection. Semua request yang melewati WAF masih divalidasi ulang di layer Pydantic sebelum menyentuh business logic.

**Input Validation**  
Pydantic validation di setiap endpoint FastAPI. Payload yang tidak sesuai schema langsung ditolak dengan HTTP 422 sebelum sampai ke service layer — ini memastikan tidak ada data berbahaya yang masuk ke DB atau model.

**Authentication**  
JWT dengan refresh token rotation. Access token TTL: 15 menit. Refresh token TTL: 7 hari. Setiap refresh token hanya bisa dipakai sekali (single-use) — mitigasi token theft.

**DDoS & MitM**  
- HTTPS enforced via HSTS header (`Strict-Transport-Security: max-age=31536000`)
- Cloudflare rate limiting + BrewStock sliding window rate limiter sebagai double protection
- CORS restricted ke origin yang terdaftar — block request dari domain tidak dikenal

**Rate Limiting: Sliding Window**  
Dipilih di atas Fixed Window karena Fixed Window punya masalah burst traffic di batas window (misalnya 100 request di detik ke-59, lalu 100 lagi di detik ke-61 = 200 request dalam 2 detik). Sliding Window menghitung jumlah request dalam window bergerak sehingga burst seperti ini tetap ter-throttle.

---

## 7. Performance & Scalability

| Masalah | Penyebab | Solusi |
|---|---|---|
| Response lambat saat traffic tinggi | Semua logic di 1 file, tanpa async | Pisah ke `routes/controllers/services/repositories`, semua endpoint `async def` |
| DB query lambat | Tidak ada indexing | Composite index `(transactionDate, skuId)` |
| Re-run model tiap request | Tidak ada caching | Redis cache hasil forecast, TTL 1 jam |
| Server down saat traffic spike | Single server | Horizontal scaling via Render atau Docker Compose multi-instance |
| Tagihan hosting naik | Over-provisioning | Cache mengurangi compute per request; scale down saat traffic rendah |

---

## 8. Frontend & UX

### Dashboard KPI Cards

Setiap card menampilkan empat elemen:

1. **Label** — nama KPI dalam bahasa yang mudah dimengerti (bukan kode teknis)
2. **Nilai saat ini** — angka aktual periode ini
3. **Perubahan vs periode lalu** — arah (naik/turun) + persentase perubahan + warna (hijau/merah)
4. **Status vs target** — badge "Di atas target" / "Perlu perhatian" / "Kritis"

Contoh tampilan keempat KPI:

```
┌─────────────────────┐  ┌─────────────────────┐
│  SKU Aktif          │  │  Total Demand       │
│  24 produk          │  │  1.240 unit         │
│  ↑ 2 vs bulan lalu  │  │  ↑ 12% vs minggu lalu│
│  Target: > 20 ✅    │  │  Target: > 1.000 ✅  │
└─────────────────────┘  └─────────────────────┘

┌─────────────────────┐  ┌─────────────────────┐
│  Total Transaksi    │  │  Rata-rata per SKU  │
│  318 transaksi      │  │  51.7 unit/SKU      │
│  ↓ 5% vs minggu lalu│  │  ↔ stabil           │
│  ⚠ Perlu perhatian  │  │  Target: > 40 ✅    │
└─────────────────────┘  └─────────────────────┘
```

Warna merah pada "↓ 5%" dan badge "⚠ Perlu perhatian" langsung menyampaikan bahwa ada yang perlu ditindaklanjuti — tanpa user harus tahu apakah 318 itu angka baik atau buruk.

### Accessibility (Lighthouse Target > 90)

- Semua elemen interaktif punya `aria-label`
- Color contrast ratio > 4.5:1 (WCAG AA compliant)
- Keyboard navigation support di semua komponen
- `role` attribute pada alert dan status badge

### CLS & LCP

- CLS < 0.1: semua chart/grafik punya dimensi fix sebelum data load (tidak ada layout shift saat data masuk)
- LCP < 2.5s: font preload via `<link rel="preload">`, komponen non-critical di-lazy load, gambar YOLO result compressed sebelum dikirim ke frontend

---

## 9. Design Patterns & Code Quality

### Patterns yang Dipakai

| Pattern | Komponen | Alasan |
|---|---|---|
| Strategy | ForecastService — pilih Prophet/XGBoost | Tambah model baru tanpa ubah service logic |
| Observer | StockAlertPublisher + StockAlertObserver | Alert bisa dikirim ke berbagai channel (log, AI, push notif) tanpa coupling |
| Factory | AiServiceFactory — pilih Claude/GPT/Noop | Ganti provider AI via env variable, tanpa ubah business logic |
| Repository | TransactionRepository | Abstraksi layer DB — kalau migrasi dari PostgreSQL ke lain, cukup ubah repository |

### SOLID Principles

- **S (Single Responsibility):** `forecastService.py` hanya urusan forecast, bukan auth atau inventory
- **O (Open/Closed):** tambah model baru (misal SARIMA) cukup tambah class baru yang implement `ForecastStrategy`, tanpa ubah `ForecastService`
- **L (Liskov Substitution):** `ClaudeAiService` dan `GptAiService` bisa saling menggantikan karena keduanya implement `AiService` abstract class
- **I (Interface Segregation):** `StockAlertObserver` hanya expose satu method `handleStockAlert` — observer tidak dipaksa implement method yang tidak dibutuhkan
- **D (Dependency Inversion):** `ForecastService` bergantung pada abstract `ForecastStrategy`, bukan pada Prophet atau XGBoost secara langsung

### Konvensi Kode

- Python: `lowerCamelCase` untuk semua variabel, konstanta, dan nama fungsi
- TypeScript/React: `lowerCamelCase` variabel, `PascalCase` komponen
- Tidak ada `snake_case` di kode baru
- Komentar: maksimal 5 kata, huruf kapital di awal kata pertama
- Bagian yang dibantu AI diberi komentar `# dibantu AI: [fungsi]`

### TDD (test driven development)

Setiap fitur baru wajib ada unit test sebelum implementasi:

```
backend/tests/
  test_forecastService.py
  test_inventoryService.py
  test_authService.py
  test_stockAlertObserver.py
```

---

## 10. Tech Stack

| Layer | Teknologi | Versi |
|---|---|---|
| Frontend | React + TypeScript | Vite 5 |
| Backend | FastAPI | Python 3.11 |
| ML Forecast | Prophet + XGBoost | prophet 1.1, xgboost 2.x |
| Vision AI | YOLOv8 (Ultralytics) | ultralytics 8.x |
| AIaaS | Claude API | claude-3-5-sonnet-latest |
| Cache | Redis | 7.x |
| Database | PostgreSQL | 15.x |
| Deploy | Render + Cloudflare | — |
| CI/CD | GitHub Actions | — |

---

## 11. CRISP-DM Mapping

| Phase | Deliverable Sistem | Deliverable Laporan |
|---|---|---|
| Business Understanding | Problem statement, KPI table | Bab 1: Latar Belakang + Problem Statement |
| Data Understanding | EDA notebook, grafik distribusi | Bab 2: Dataset + EDA (grafik wajib) |
| Data Preparation | Script cleaning + feature engineering | Bab 3: Perbandingan raw vs clean data |
| Modelling | Prophet + XGBoost trained, YOLO fine-tuned | Bab 4: Arsitektur + hyperparameter + training curve |
| Evaluation | MAPE, RMSE, F1-Score, actual vs predicted | Bab 5: Visualisasi evaluasi + analisis |
| Deployment | FastAPI + React live di Render/Vercel | Bab 6: Use case diagram + screenshot fitur |

---

## 12. Struktur Folder

```
BrewStock/
├── backend/
│   └── src/app/
│       ├── controllers/
│       ├── core/           # config, settings
│       ├── factories/      # AiServiceFactory
│       ├── models/         # Pydantic data models
│       ├── observers/      # stockAlertObserver, aiStockObserver
│       ├── repositories/   # TransactionRepository
│       ├── routes/         # authRoutes, forecastRoutes, inventoryRoutes
│       ├── schemas/        # request/response schemas
│       ├── services/       # forecastService, inventoryService, authService
│       │   └── ai/         # claudeAiService, gptAiService, noopAiService
│       ├── strategies/     # ProphetStrategy, XGBoostStrategy
│       └── main.py
├── frontend/
│   └── src/
│       ├── components/     # KpiCard, AlertBadge, ForecastChart
│       ├── pages/          # Dashboard, Inventory, Assistant
│       ├── hooks/          # useForecast, useInventory
│       ├── api.ts
│       └── types.ts
├── ml/
│   └── forecast/
│       ├── data/
│       │   ├── raw/coffee-shop/
│       │   └── processed/
│       └── notebooks/
│           ├── coffeeShopSalesReference.ipynb
│           └── demandForecastStarter.ipynb
├── infra/
├── PRD.md
├── render.yaml
└── README.md
```

---

## 13. Roadmap Development

| Minggu | Target | Status |
|---|---|---|
| W6 | Proposal + video YouTube | Selesai |
| W8–9 | Backend auth, forecast service, unit test | Selesai |
| W10–11 | EDA notebook, model Prophet + XGBoost, evaluasi | In Progress |
| W12 | Demo: forecast endpoint live + prototype frontend | Target demo luring |
| W13 | YOLO fine-tune + Claude integration end-to-end | Planned |
| W14 | Frontend 4 fitur lengkap, Lighthouse check | Planned |
| W15 | Deploy final, laporan, video presentasi | Deadline 24 Mei 2026 |

## ADDENDUM — Scanner Module

> Tambahan dari PRD v2.0. Komponen ini memenuhi spesifikasi "AI Bebas" pada Tugas Besar II4012.

---

### S1. Konteks & Justifikasi YOLO

Masalah yang diserang: barista harus hitung stok manual setiap hari — error-prone dan butuh ~15 menit. Scanner menggantikan ini dengan foto + deteksi otomatis dalam < 5 detik.

**Kenapa YOLO, bukan OCR atau barcode?**  
Barcode butuh label fisik di setiap item — tidak realistis untuk bahan baku seperti kantong susu atau botol sirup yang sering tidak berlabel. OCR hanya baca teks, tidak bisa hitung jumlah objek. YOLO secara langsung mendeteksi dan menghitung jumlah instance per kelas dalam satu gambar.

**Kenapa YOLOv8n, bukan YOLOv8x atau YOLOv9?**  
YOLOv8n (nano) dipilih karena inference time-nya < 30ms di CPU biasa — tidak butuh GPU khusus untuk demo. YOLOv8x lebih akurat tapi butuh GPU atau inference akan timeout di server Render free tier. Untuk dataset kecil (< 500 gambar), perbedaan akurasi antara nano dan large tidak signifikan.

---

### S2. Dataset Strategy

Tidak ada dataset publik khusus "bahan kopi coffee shop." Strategi bertingkat:

| Tier | Sumber | Estimasi Gambar | Dipakai Untuk |
|---|---|---|---|
| 1 | Roboflow Universe — cari "coffee ingredients", "milk bottle", "syrup bottle" | ~150–300 per class | Fine-tuning base |
| 2 | Foto manual dari coffee shop / dapur | 30–50 per class | Domain adaptation |
| 3 | Data augmentation (Ultralytics built-in) | 3–5x lipat dari tier 1+2 | Reach minimum threshold |

**Kelas yang dideteksi (minimum viable):**

```
classes:
  0: milk_bottle     # susu kotak/botol
  1: syrup_bottle    # sirup flavor (hazelnut, vanilla, dll)
  2: coffee_bag      # kantong biji kopi / kopi bubuk
  3: whipped_cream   # kaleng whipped cream
  4: cup_stack       # tumpukan gelas/cup
```

Lima kelas ini cover bahan paling kritikal di coffee shop UMKM. Tambah kelas lain setelah F1-Score baseline tercapai.

**Format label:** YOLO format (`.txt` per gambar, normalized xywh)

```
# Format tiap baris di label file
<class_id> <x_center> <y_center> <width> <height>
# Contoh: milk_bottle di tengah frame
0 0.512 0.438 0.124 0.203
```

---

### S3. Training Pipeline

```
Dataset (Roboflow + manual foto)
  → split: train 70% / val 20% / test 10%
  → augmentation via Ultralytics (flip, brightness ±30%, mosaic)
  → fine-tune YOLOv8n pretrained COCO
      epochs: 50–100 (early stopping patience=10)
      imgsz: 640
      batch: 16
      optimizer: AdamW, lr0=0.001
  → evaluate: mAP@0.5, F1 per class, confusion matrix
  → export: best.pt → backend/ml/scanner/models/
```

**Hyperparameter yang perlu di-report di laporan:**

| Param | Nilai | Alasan |
|---|---|---|
| `imgsz` | 640 | Standard YOLO, balance antara akurasi dan kecepatan |
| `conf` threshold | 0.4 | Lebih rendah dari default 0.25 agar tidak terlalu banyak false negative |
| `iou` threshold | 0.5 | mAP@0.5, standard evaluasi COCO |
| `epochs` | 50 + early stopping | Hindari overfitting pada dataset kecil |

---

### S4. Backend — Scanner Service

#### Struktur File Baru

```
backend/src/app/
├── controllers/
│   └── scannerController.py   # NEW
├── routes/
│   └── scannerRoutes.py       # NEW
├── services/
│   └── scannerService.py      # NEW
├── schemas/
│   └── scannerSchema.py       # NEW
└── models/
    └── scannerResultModel.py  # NEW

backend/ml/scanner/
└── models/
    └── best.pt                # YOLO weights (gitignored)
```

#### API Endpoint

```
POST /api/v1/scanner/detect
Content-Type: multipart/form-data

Request:
  image: File (JPEG/PNG, max 10MB)

Response 200:
{
  "detections": [
    {
      "className": "milk_bottle",
      "confidence": 0.87,
      "count": 3,
      "boundingBoxes": [
        {"x1": 120, "y1": 80, "x2": 245, "y2": 310},
        ...
      ]
    }
  ],
  "totalItemsDetected": 8,
  "annotatedImageBase64": "data:image/jpeg;base64,...",
  "inferenceTimeMs": 28,
  "suggestedStockUpdate": [
    {"skuId": "milk-full-cream", "detectedCount": 3}
  ]
}
```

#### scannerService.py — Logic

```python
# Tanggung jawab ScannerService:
# 1. Load model (sekali saat startup, bukan per request — pakai singleton)
# 2. Run inference pada gambar yang di-upload
# 3. Parse detection result ke format response
# 4. Map class name ke skuId yang ada di DB
# 5. Return annotated image (bounding box di-draw di sini)

class ScannerService:
    _modelInstance = None  # Singleton — load sekali

    @classmethod
    def getInstance(cls, modelPath: str) -> "ScannerService":
        if cls._modelInstance is None:
            cls._modelInstance = cls(modelPath)
        return cls._modelInstance

    def __init__(self, modelPath: str) -> None:
        from ultralytics import YOLO
        self.model = YOLO(modelPath)
        self.classToSkuMap = {
            "milk_bottle": "milk-full-cream",
            "syrup_bottle": "syrup-hazelnut",
            "coffee_bag": "coffee-arabica",
            "whipped_cream": "whipped-cream-can",
            "cup_stack": "cup-medium",
        }

    # dibantu AI: runDetection
    async def runDetection(self, imageBytes: bytes) -> ScannerResult:
        ...
```

**Kenapa Singleton untuk model?**  
YOLO model loading butuh ~1–2 detik dan ~200MB memory. Kalau di-load per request, setiap scan akan spike memory dan latency. Singleton memastikan model dimuat sekali saat startup dan di-reuse untuk semua request — pattern yang sama dengan bagaimana production ML inference server bekerja (TorchServe, Triton Inference Server).

#### Security untuk File Upload

```python
# Validasi di controller sebelum masuk service
ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10MB

# Cek magic bytes, BUKAN hanya extension
# Extension bisa dipalsukan: evil.exe rename jadi evil.jpg
import imghdr
imageType = imghdr.what(None, h=imageBytes[:32])
if imageType not in {"jpeg", "png", "webp"}:
    raise HTTPException(status_code=415, detail="Unsupported file type")
```

#### Rate Limiting Khusus Scanner

Scanner endpoint lebih berat dari endpoint lain (YOLO inference). Terapkan limit lebih ketat:

```
Scanner endpoint: 10 req/min per user (bukan 100 req/min global)
Reason: 1 inference ~28ms CPU tapi spike memory ~200MB
        10 concurrent requests = ~2GB memory → Render free tier crash
```

---

### S5. Frontend — Scanner Page

#### Komponen Hierarchy

```
ScannerPage
├── ImageUploadZone          # drag-drop atau click-to-upload
├── ScanResultOverlay        # annotated image dengan bounding box
│   └── DetectionBadge[]     # per-class count badge overlay
├── DetectionSummaryCard[]   # list per kelas: nama, count, confidence
├── StockUpdatePreview       # tabel "Stok sekarang → Setelah scan"
└── ConfirmStockUpdate       # tombol konfirmasi update stok ke DB
```

#### UX Flow

```
User upload foto rak/kulkas
  → Loading spinner (max 5 detik, dengan progress indicator)
  → Tampilkan annotated image (bounding box berwarna per kelas)
  → Tampilkan DetectionSummaryCard per kelas:
       "Susu Full Cream: 3 botol terdeteksi (confidence: 87%)"
  → Tampilkan StockUpdatePreview:
       "Stok saat ini: 5 | Terdeteksi: 3 | Update ke: 3?"
  → Tombol "Konfirmasi Update Stok" → PATCH /inventory/{skuId}
  → Toast notification: "Stok berhasil diperbarui"
```

**Kenapa ada konfirmasi sebelum update stok?**  
YOLO tidak 100% akurat — false detection bisa terjadi. Langsung auto-update stok tanpa konfirmasi berisiko memasukkan data salah ke DB. Pattern "human-in-the-loop" ini adalah best practice untuk AI yang berinteraksi dengan data operasional.

#### Accessibility & Performance

```tsx
// ImageUploadZone — accessibility
<div
  role="button"
  aria-label="Upload foto stok — klik atau drag gambar ke sini"
  tabIndex={0}
  onKeyDown={handleKeyboardActivation}
  style={{ width: "100%", height: "300px" }}  // fixed height — prevent CLS
>
```

- Annotated image: dimensi fixed `640x640` container, image di-fit-contain — tidak ada layout shift
- Loading state: skeleton placeholder dengan dimensi sama dengan result — CLS = 0
- Bounding box overlay: canvas element di atas gambar, z-index managed

---

### S6. Integrasi ke InventoryService

Scanner tidak langsung update DB — ia membuat `SuggestedStockUpdate` yang kemudian dikonfirmasi user dan dikirim ke endpoint yang sudah ada:

```
ScannerService.runDetection()
  → return suggestedStockUpdate: [{ skuId, detectedCount }]

User konfirmasi di frontend
  → PATCH /api/v1/inventory/{skuId}/stock
  → InventoryService.updateCurrentStock(skuId, newCount)
```

Ini memisahkan concern scanning (ScannerService) dari concern inventory management (InventoryService) — Single Responsibility Principle terjaga.

---

### S7. Evaluasi untuk Laporan

**Metrik wajib di laporan:**

| Metrik | Target | Cara Hitung |
|---|---|---|
| mAP@0.5 | > 0.80 | Ultralytics auto-generate saat training |
| F1-Score per class | > 0.85 per class | Dari confusion matrix post-training |
| Precision | > 0.85 | TP / (TP + FP) |
| Recall | > 0.80 | TP / (TP + FN) |
| Inference time | < 100ms | Timer di `runDetection()` |

**Visualisasi wajib di notebook (untuk laporan):**

1. Training curve: `results.png` dari Ultralytics (mAP vs epoch)
2. Confusion matrix: `confusion_matrix.png`
3. Sample prediction: gambar dengan bounding box, label, confidence
4. PR curve per class

**Interpretasi yang diharapkan di laporan:**  
Jelaskan kenapa kelas tertentu punya F1 lebih rendah (misalnya `cup_stack` sulit karena tumpukan objek overlapping). Ini bukan kelemahan — ini menunjukkan pemahaman tentang limitation model.

---

### S8. Copilot Prompt untuk Scanner

Tambahkan item 7 dan 8 ke prompt utama setelah item 1–6 selesai:

```
@workspace

Items 1-6 are done. Now implement item 7:

ITEM 7 — Backend Scanner Service:
- New files: scannerService.py, scannerController.py,
  scannerRoutes.py, scannerSchema.py
- Singleton pattern for YOLO model loading (load once on startup)
- POST /api/v1/scanner/detect — accept multipart/form-data image
- Validate file by magic bytes (not extension), reject non-image
- Run YOLOv8 inference, return: detections per class (count +
  bounding boxes), annotated image as base64, inferenceTimeMs,
  suggestedStockUpdate mapped to skuId
- Rate limit: 10 req/min per user (separate from global 100/min)
- Model path from settings (env var YOLO_MODEL_PATH)
- Unit test: mock YOLO, test schema validation + rate limit

ITEM 8 — Frontend Scanner Page:
- ScannerPage with: ImageUploadZone (drag-drop, click),
  ScanResultOverlay (annotated image + bbox canvas overlay),
  DetectionSummaryCard per class, StockUpdatePreview table,
  ConfirmStockUpdate button → PATCH inventory endpoint
- All containers fixed height to prevent CLS
- aria-label on all interactive elements
- Loading: skeleton placeholder same size as result
- On confirm: call PATCH /api/v1/inventory/{skuId}/stock
  then show toast notification

Follow all existing conventions: lowerCamelCase Python,
PascalCase components, add "dibantu AI" comments.
Do item 7 first.
```