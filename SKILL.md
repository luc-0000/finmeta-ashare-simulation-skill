---
name: finmeta-simulation-skill
description: Unified simulation trading skill. Supports A-Share and Crypto markets — market data, account queries, trading (buy/sell), and order history. Use when the user wants to check prices, analyze charts, manage simulation accounts, or place trades in either market.
---

# FinMeta Simulation Trading

Covers **A-Share** (`ashare/`) and **Crypto** (`crypto/`). Each sub-module has its own `api.py` and `api_reference.md`.

## Quick Start

```bash
export FINTOOLS_API_TOKEN="your-token"
export FINTOOLS_SIMULATION_ACCOUNT_ID=123   # A-Share only

# A-Share
python ashare/api.py --action get_quote --symbols "600519.SH"
python ashare/api.py --action account
python ashare/api.py --action buy --symbol 600519.SH --quantity 100

# Crypto
python crypto/api.py --action get_quotes --symbols "BTC/USDT,ETH/USDT"
python crypto/api.py --action account
python crypto/api.py --action buy --symbol BTC/USDT --quantity 0.01
```

## Setup

```bash
# Save credentials (shared config.json at skill root)
python ashare/api.py --token YOUR_TOKEN --account-id 123
python crypto/api.py --token YOUR_TOKEN
```

- **Token**: Profile page → Access Token
- **Account ID** (A-Share only): My Simulation → click ID chip to copy

## Tools

### A-Share (`ashare/api.py`)

| Action | Command |
|--------|---------|
| Stock list | `--action list_stocks` |
| Quote | `--action get_quote --symbols "600519.SH"` |
| K-line | `--action kline --symbol 600519.SH` |
| Account | `--action account` |
| Positions | `--action positions` |
| Buy | `--action buy --symbol 600519.SH --quantity 100` |
| Sell | `--action sell --symbol 600519.SH --quantity 100` |
| Orders | `--action orders` |
| Balance log | `--action balance_log` |
| Fee log | `--action fee_log` |
| Rules | `--action rules` |

### Crypto (`crypto/api.py`)

| Action | Command |
|--------|---------|
| Symbol list | `--action list_symbols` |
| Quotes | `--action get_quotes --symbols "BTC/USDT"` |
| K-line | `--action kline --symbol BTC/USDT` |
| Account | `--action account` |
| Positions | `--action positions` |
| Buy | `--action buy --symbol BTC/USDT --quantity 0.01` |
| Sell | `--action sell --symbol BTC/USDT --quantity 0.01` |
| Orders | `--action orders` |
| Balance log | `--action balance_log` |
| Rules | `--action rules` |

## Agent Notes

### First Run — Token & Account Setup

1. Check if `FINTOOLS_API_TOKEN` env var is set, or `config.json` has `token`
2. For A-Share: check `FINTOOLS_SIMULATION_ACCOUNT_ID` env var or `config.json` `account_id`
3. If token is missing:
   - Ask: *"I need your API token. Get it from Profile → Access Token."*
   - Save with: `python ashare/api.py --token <token>`
4. If A-Share account_id is missing (but token is set):
   - List accounts: `curl -H "Authorization: Bearer $TOKEN" https://fin-meta.net/api/v1/ashare/accounts?lightweight=true`
   - Present the list: *"Here are your accounts: (1) Account #123 — A-Share. Which one?"*
   - Save with: `python ashare/api.py --account-id <id>`
5. Crypto does not need account_id — it auto-resolves from your user.

### Typical Flow

```bash
# A-Share
python ashare/api.py --action get_quote --symbols "600519.SH"
python ashare/api.py --action account
python ashare/api.py --action buy --symbol 600519.SH --quantity 100

# Crypto
python crypto/api.py --action get_quotes --symbols "BTC/USDT"
python crypto/api.py --action account
python crypto/api.py --action buy --symbol BTC/USDT --quantity 0.01
```

### Python Import (Agent Code)

```python
from finmeta_simulation_skill.ashare import buy as ashare_buy, get_account as ashare_account
from finmeta_simulation_skill.crypto import buy as crypto_buy, get_account as crypto_account

# A-Share — account_id optional (reads from env var / config.json)
result = ashare_buy("600519.SH", 100, account_id=123)

# Crypto — no account_id needed
result = crypto_buy("BTC/USDT", 0.01)
```
