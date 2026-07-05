---
name: finmeta-ashare-simulation-skill
description: A-Share simulation trading. Supports market data (list_stocks/get_quote/kline), account (account/positions), trading (buy/sell), history (orders_history/buy_list/sell_list/balance_log/fee_log), and rules. Use when the user wants to check A-Share prices, analyze K-line charts, manage simulation accounts, buy/sell stocks, or query trade history.
---

# A-Share Simulation Trading

## Quick Start

Get your API token from **Profile** (user dropdown → Profile). Then:

```bash
export FINTOOLS_API_TOKEN="your-token"

python trading_api.py --action get_quote --symbols "600519.SH"
python trading_api.py --action kline --stock-code 600519.SH
python trading_api.py --action account
python trading_api.py --action buy --stock-code 600519.SH --quantity 100
```

The script auto-installs `requests` if missing. Nothing else to do.

## Token

One token, two ways:

```bash
export FINTOOLS_API_TOKEN="your-token"   # env var (recommended)
python trading_api.py --token your-token # saves to config.json
```

Get the token from your Profile page: user dropdown (top-right) → Profile → Access Token.

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

### First Run — Token Setup

Before running any command, check for credentials:

1. Check if `FINTOOLS_API_TOKEN` env var is set
2. Check if `config.json` in the skill directory exists and contains a `token` field
3. If neither is found:
   - Ask the user: *"I need your API token to access Fintools. Get it from your Profile page (user dropdown → Profile → Access Token). Would you like to provide it?"*
   - If the user provides a token, run: `python trading_api.py --token <token>` to save it
   - Confirm the token works with `python trading_api.py --action account`

### Typical Flow

```bash
python trading_api.py --action get_quote --symbols "600519.SH"
python trading_api.py --action kline --stock-code 600519.SH
python trading_api.py --action account
python trading_api.py --action buy --stock-code 600519.SH --quantity 100
python trading_api.py --action orders_history
```
