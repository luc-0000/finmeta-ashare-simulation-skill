# Crypto Simulation API Reference

Base: `https://fin-meta.net/api/v1/crypto`

## Market Data (no auth)

| Action | HTTP | Path |
|--------|------|------|
| list_symbols | GET | /symbols |
| get_quotes | GET | /quotes?symbols= |
| kline | GET | /kline?symbol=&limit= |

## Account / Trading (Bearer Token required)

| Action | HTTP | Path | Body |
|--------|------|------|------|
| account | GET | /account | — |
| buy | POST | /orders/buy | {symbol, quantity} |
| sell | POST | /orders/sell | {symbol, quantity} |

## History (Bearer Token required)

| Action | HTTP | Path |
|--------|------|------|
| orders | GET | /orders?limit= |
