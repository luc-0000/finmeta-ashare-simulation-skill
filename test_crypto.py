#!/usr/bin/env python3
"""Quick smoke test for crypto simulation trading — uses the skill's own API functions."""
import os, sys, json

# Point to the skill root so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Override API base to local backend for testing
os.environ.setdefault("FINTOOLS_API_BASE", "http://localhost:8000")

from crypto.api import list_symbols, get_quotes, get_kline, get_account, buy, sell, get_orders

# ── Use a token from env or config.json ──
from crypto.api import _load_token, _save_token

token = _load_token()
if not token:
    print("No token found in env vars or config.json.")
    print("Set FINTOOLS_API_TOKEN or run: python crypto/api.py --token YOUR_TOKEN")
    sys.exit(1)

print("=" * 60)
print("Crypto Simulation Smoke Test")
print("=" * 60)

# 1. List Symbols
print("\n1. list_symbols()")
r = list_symbols()
if r.get("success"):
    data = r["data"].get("data", [])
    print(f"   OK — {len(data)} symbols, first 3: {[s['symbol'] for s in data[:3]]}")
else:
    print(f"   FAIL — {r.get('error')}")
    sys.exit(1)

# 2. Get Quotes (BTC & ETH)
print("\n2. get_quotes('BTC/USDT,ETH/USDT')")
r = get_quotes("BTC/USDT,ETH/USDT")
if r.get("success"):
    quotes = r["data"].get("data", {})
    for sym, q in quotes.items():
        print(f"   OK — {sym}: ${q.get('price', 'N/A')}")
else:
    print(f"   FAIL — {r.get('error')}")

# 3. Kline
print("\n3. get_kline('BTC/USDT', limit=5)")
r = get_kline("BTC/USDT", limit=5)
if r.get("success"):
    kdata = r["data"].get("data", {}).get("kline", [])
    print(f"   OK — {len(kdata)} candles")
else:
    print(f"   FAIL — {r.get('error')}")

# 4. Account
print("\n4. get_account()")
r = get_account()
if r.get("success"):
    acc = r["data"].get("data", {})
    print(f"   OK — balance: ${acc.get('current_balance', 'N/A')}, "
          f"total_assets: ${acc.get('total_assets', 'N/A')}, "
          f"P/L: {acc.get('total_profit', 'N/A')}")
else:
    print(f"   FAIL — {r.get('error')}")
    sys.exit(1)

# 5. Buy (small test quantity)
print("\n5. buy('BTC/USDT', 0.001)")
r = buy("BTC/USDT", 0.001)
if r.get("success"):
    result = r["data"].get("data", r["data"])
    print(f"   OK — order placed: {json.dumps(result, default=str)[:200]}")
else:
    print(f"   FAIL — {r.get('error')} (this is OK if account check fails)")

# 6. Sell (very small test quantity)
print("\n6. sell('BTC/USDT', 0.0001)")
r = sell("BTC/USDT", 0.0001)
if r.get("success"):
    result = r["data"].get("data", r["data"])
    print(f"   OK — order placed: {json.dumps(result, default=str)[:200]}")
else:
    print(f"   FAIL — {r.get('error')} (may be expected)")

# 7. Order History
print("\n7. get_orders(limit=10)")
r = get_orders(10)
if r.get("success"):
    raw = r["data"].get("data", r["data"])
    if isinstance(raw, list):
        orders = raw
    elif isinstance(raw, dict):
        orders = raw.get("orders", raw.get("items", []))
    else:
        orders = []
    if isinstance(orders, list):
        print(f"   OK — {len(orders)} orders")
        for o in orders[:3]:
            print(f"      {o.get('side', '?'):4s} {o.get('symbol', '?'):12s} "
                  f"qty={o.get('quantity', '?')} @ {o.get('price', '?')} "
                  f"status={o.get('status', '?')}")
    else:
        print(f"   OK — response: {json.dumps(orders, default=str)[:200]}")
else:
    print(f"   FAIL — {r.get('error')}")

print("\n" + "=" * 60)
print("Smoke test complete")
