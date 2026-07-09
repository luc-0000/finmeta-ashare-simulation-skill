# A-Share Simulation API Reference (v3 — per-account routing)

Backend default: `https://fin-meta.net`. Override via `FINTOOLS_API_BASE` env var. Auth via `FINTOOLS_API_TOKEN` (from Profile page). All account/trading/history endpoints require `FINTOOLS_SIMULATION_ACCOUNT_ID` env var (from My Simulation page — click the ID chip to copy).

## Endpoints

### Market Data (no auth)

| Action | HTTP | Path |
|--------|------|------|
| list_stocks | GET | /api/v1/ashare/stocks |
| get_quote | GET | /api/v1/ashare/stocks/quotes?symbols= |
| kline | GET | /api/v1/ashare/stocks/{code}/kline?period=1d&limit=60 |
| rules | GET | /api/v1/ashare/rules |

### Account / Trading (Bearer Token + Account ID required)

All paths include `{account_id}` — get yours from My Simulation page.

| Action | HTTP | Path | Body |
|--------|------|------|------|
| account | GET | /api/v1/ashare/accounts/{account_id} | — |
| positions | GET | /api/v1/ashare/accounts/{account_id}/positions | — |
| buy | POST | /api/v1/ashare/accounts/{account_id}/orders/buy | {stock_code, quantity} |
| sell | POST | /api/v1/ashare/accounts/{account_id}/orders/sell | {stock_code, quantity} |

### History (Bearer Token + Account ID required)

| Action | HTTP | Path |
|--------|------|------|
| orders_history | GET | /api/v1/ashare/accounts/{account_id}/orders |
| buy_list | GET | /api/v1/ashare/accounts/{account_id}/orders?side=buy&page=&limit= |
| sell_list | GET | /api/v1/ashare/accounts/{account_id}/orders?side=sell&page=&limit= |
| balance_log | GET | /api/v1/ashare/accounts/{account_id}/balance-log?page=&limit= |
| fee_log | GET | /api/v1/ashare/accounts/{account_id}/balance-log |

## Config Format (config.json)

```json
{"token": "your-api-token", "account_id": 123}
```

## Response Format

```json
{"code": 0, "msg": "ok", "data": {...}}
```

Errors: HTTP 400 (detail) or 401 (unauthorized).
