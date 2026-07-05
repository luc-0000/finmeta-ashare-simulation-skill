# A-Share Simulation API Reference

Backend default: `https://fin-meta.net`. Override via `FINTOOLS_API_BASE` env var. Auth via `FINTOOLS_API_TOKEN` (from Profile page).

## Endpoints

### Market Data (no auth)

| Action | HTTP | Path |
|--------|------|------|
| list_stocks | GET | /api/v1/ashare/stocks |
| get_quote | GET | /api/v1/ashare/stocks/quotes?symbols= |
| kline | GET | /api/v1/ashare/stocks/{code}/kline?period=1d&limit=60 |
| rules | GET | /api/v1/ashare/rules?market= |

### Account / Trading (Bearer Token required)

| Action | HTTP | Path | Body |
|--------|------|------|------|
| account | GET | /api/v1/ashare/account?market= | — |
| positions | GET | /api/v1/ashare/positions?market= | — |
| buy | POST | /api/v1/ashare/orders/buy | {stock_code, quantity} |
| sell | POST | /api/v1/ashare/orders/sell | {stock_code, quantity} |

### History (Bearer Token required)

| Action | HTTP | Path |
|--------|------|------|
| orders_history | GET | /api/v1/ashare/orders?market= |
| buy_list | GET | /api/v1/ashare/orders/buy?page=&limit= |
| sell_list | GET | /api/v1/ashare/orders/sell?page=&limit= |
| balance_log | GET | /api/v1/ashare/balance-log?page=&limit= |
| fee_log | GET | /api/v1/ashare/balance-log |

## Response Format

```json
{"code": 0, "msg": "ok", "data": {...}}
```

Errors: HTTP 400 (detail) or 401 (unauthorized).
