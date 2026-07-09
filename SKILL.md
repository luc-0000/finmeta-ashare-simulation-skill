---
name: finmeta-ashare-simulation-skill
description: A-Share simulation trading. Supports market data (list_stocks/get_quote/kline), account (account/positions), trading (buy/sell), history (orders_history/buy_list/sell_list/balance_log/fee_log), and rules. Use when the user wants to check A-Share prices, analyze K-line charts, manage simulation accounts, buy/sell stocks, or query trade history.
---

# A-Share Simulation Trading

## Quick Start

Get your API token from **Profile** (user dropdown → Profile) and your **Account ID** from **My Simulation** (click the ID chip to copy). Then:

```bash
export FINTOOLS_API_TOKEN="your-token"
export FINTOOLS_SIMULATION_ACCOUNT_ID=123

python trading_api.py --action get_quote --symbols "600519.SH"
python trading_api.py --action kline --stock-code 600519.SH
python trading_api.py --action account
python trading_api.py --action buy --stock-code 600519.SH --quantity 100
```

The script auto-installs `requests` if missing. Nothing else to do.

## Setup

Two pieces of config, two ways:

```bash
# env var (recommended)
export FINTOOLS_API_TOKEN="your-token"
export FINTOOLS_SIMULATION_ACCOUNT_ID=123

# one-time save to config.json
python trading_api.py --token your-token --account-id 123
```

- **Token**: Profile page → Access Token
- **Account ID**: My Simulation → click the ID chip on any account card to copy

## Tools

### Market Data

| Action | Command |
|--------|---------|
| Stock list | `--action list_stocks` |
| Quote | `--action get_quote --symbols "600519.SH"` |
| K-line | `--action kline --stock-code 600519.SH` |

### Account

| Action | Command |
|--------|---------|
| Account | `--action account` |
| Positions | `--action positions` |

### Trading

| Action | Command |
|--------|---------|
| Buy | `--action buy --stock-code 600519.SH --quantity 100` |
| Sell | `--action sell --stock-code 600519.SH --quantity 100` |

### History

| Action | Command |
|--------|---------|
| All orders | `--action orders_history` |
| Buy history | `--action buy_list` |
| Sell history | `--action sell_list` |
| Balance log | `--action balance_log` |
| Fee log | `--action fee_log` |

### Rules

| Action | Command |
|--------|---------|
| Trading rules | `--action rules` |

## Rules Summary

- Lot size: 100 shares, T+1 settlement
- Price limits: ±10% main board, ±20% ChiNext/STAR, ±30% Beijing Exchange
- Commission: 0.025% (min ¥5), Stamp tax: 0.05% (sell only)
- Max ¥500,000 per order, 200 orders/day
- Initial balance: ¥1,000,000

## Agent Notes

### First Run — Token & Account Setup

Before running any command, check for credentials:

1. Check if `FINTOOLS_API_TOKEN` env var is set, or if `config.json` has a `token` field
2. Check if `FINTOOLS_SIMULATION_ACCOUNT_ID` env var is set, or if `config.json` has an `account_id` field
3. If either is missing:
   - **Token**: Ask the user: *"I need your API token to access Fintools. Get it from your Profile page (user dropdown → Profile → Access Token)."*
   - **Account ID**: Ask the user: *"Which simulation account should I trade with? Go to My Simulation, find the account you want to use, and copy its ID (click the ID chip on the account card). What's the account ID?"*
   - Save both with: `python trading_api.py --token <token> --account-id <id>`
   - Confirm it works with `python trading_api.py --action account`

### Typical Flow

```bash
python trading_api.py --action get_quote --symbols "600519.SH"
python trading_api.py --action kline --stock-code 600519.SH
python trading_api.py --action account
python trading_api.py --action buy --stock-code 600519.SH --quantity 100
python trading_api.py --action orders_history
```

### Python Import (Agent Code)

```python
from finmeta_ashare_simulation_skill import buy_stock, get_account_snapshot

# Each function accepts an optional account_id parameter
result = buy_stock("600519.SH", 100, account_id=123)
snapshot = get_account_snapshot(account_id=123)
```

When `account_id` is omitted, the function reads from `FINTOOLS_SIMULATION_ACCOUNT_ID` env var or `config.json`.
