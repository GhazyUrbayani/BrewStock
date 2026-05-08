# BrewStock API

## Health
- `GET /health`

## Auth
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`

## Inventory
- `GET /api/v1/inventory/summary`
- `GET /api/v1/inventory/transactions?skuId=<sku>&limit=100`
- `POST /api/v1/inventory/transactions`
- `DELETE /api/v1/inventory/transactions/{transactionId}`

## Forecast
- `POST /api/v1/forecast/demand`

## Scanner
- `POST /api/v1/scanner/detect` (`multipart/form-data`, field `image`, optional `applyStockUpdate`)

Headers:
- `Authorization: Bearer <accessToken>`

Rate limit:
- `100 request/menit/IP`
- `10 request/menit/user` untuk scanner
