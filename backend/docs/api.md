# BrewStock API

## Auth
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`

## Forecast
- `POST /api/v1/forecast/demand`

Headers:
- `Authorization: Bearer <accessToken>`

Rate limit:
- `100 request/menit/IP`
