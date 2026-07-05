# FinMeta A-Share Simulation Trading

A-Share (A股) simulation trading CLI. Query market data, manage a virtual account, and place buy/sell orders — all from the command line.

## Quick Start

```bash
git clone https://github.com/luc-0000/finmeta-ashare-simulation-skill.git
cd finmeta-ashare-simulation-skill

# Public data — no token needed
python trading_api.py --action get_quote --symbols "600519.SH"

# Trading — get your token from https://fin-meta.net/profile
export FINTOOLS_API_TOKEN="your-token"
python trading_api.py --action account
python trading_api.py --action buy --stock-code 600519.SH --quantity 100
```

See [SKILL.md](SKILL.md) for the full command reference.
