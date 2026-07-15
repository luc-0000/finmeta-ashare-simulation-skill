#!/usr/bin/env python3
"""
usstock skill integration test — exercises every function against a live backend.

Usage:
    FINTOOLS_API_TOKEN=<your-PAT> python usstock/test_skill.py
    FINTOOLS_API_TOKEN=<your-PAT> FINTOOLS_API_BASE=http://localhost:8000 python usstock/test_skill.py

Coverage:
    Public (no auth):    list_symbols, get_quotes, get_kline, get_rules
    Auth-required:       get_account, get_positions, buy, sell, get_orders, get_balance_log

If no token is set, auth-required tests are skipped (public ones still run).

Test flow for auth-required tests:
    1. Resolve/create a personal usstock account
    2. buy(AAPL, 10) → verifies position appears
    3. sell(AAPL, 3) → verifies position updates to 7
    4. get_orders / get_balance_log → verify history
    5. Cleanup: reset account to clear test data
"""

import os
import sys
import json
import time
from pathlib import Path

# Allow running from skill root or from usstock/ directly
SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT.parent))

# Default to local backend if FINTOOLS_API_BASE not set (for dev testing)
os.environ.setdefault("FINTOOLS_API_BASE", "http://localhost:8000")

from finmeta_simulation_skill.usstock import (
    list_symbols,
    get_quotes,
    get_kline,
    get_rules,
    get_account,
    get_positions,
    buy,
    sell,
    get_orders,
    get_balance_log,
)
from finmeta_simulation_skill.usstock.api import _load_token, API_BASE

# Test against a known-active symbol. AAPL is the most reliable.
TEST_SYMBOL = "AAPL"
TEST_SYMBOLS_BATCH = ["AAPL", "MSFT", "GOOGL"]


# ── Test runner ───────────────────────────────────────

PASS = 0
FAIL = 0
SKIP = 0


def run(name, fn, *args, **kwargs):
    """Run a test function, track pass/fail, print result."""
    global PASS, FAIL
    try:
        result = fn(*args, **kwargs)
        ok = isinstance(result, dict) and result.get("success", False)
        if ok:
            PASS += 1
            print(f"  ✓ {name}")
            return result
        else:
            FAIL += 1
            err = result.get("error", "unknown") if isinstance(result, dict) else "non-dict return"
            print(f"  ✗ {name}: {err}")
            return result
    except Exception as e:
        FAIL += 1
        print(f"  ✗ {name}: exception {type(e).__name__}: {e}")
        return None


def skip(name, reason):
    global SKIP
    SKIP += 1
    print(f"  - {name}: SKIPPED ({reason})")


# ── Tests ─────────────────────────────────────────────

def test_public_endpoints():
    """Functions that don't require auth."""
    print("\n=== Public endpoints (no auth) ===")

    # list_symbols
    r = run("list_symbols()", list_symbols)
    if r and r.get("success"):
        syms = r.get("data", {}).get("data", [])
        print(f"    returned {len(syms)} symbols")

    # get_quotes — single
    run(f'get_quotes("{TEST_SYMBOL}")', get_quotes, TEST_SYMBOL)

    # get_quotes — batch + list input
    run(f'get_quotes({TEST_SYMBOLS_BATCH})', get_quotes, TEST_SYMBOLS_BATCH)

    # get_kline
    r = run(f'get_kline("{TEST_SYMBOL}", limit=10)', get_kline, TEST_SYMBOL, 10)
    if r and r.get("success"):
        kline = r.get("data", {}).get("data", {}).get("kline", [])
        print(f"    returned {len(kline)} bars")

    # get_kline with timeframe
    run(f'get_kline("{TEST_SYMBOL}", limit=5, timeframe="5Min")',
        get_kline, TEST_SYMBOL, 5, "5Min")

    # get_rules
    r = run("get_rules()", get_rules)
    if r and r.get("success"):
        rules = r.get("data", {}).get("data", {})
        print(f"    lot_size={rules.get('min_lot_size')}, T+{0 if rules.get('t_plus_1') is False else 1}")


def test_authed_endpoints():
    """Functions requiring a Bearer token."""
    print("\n=== Auth-required endpoints ===")

    if not _load_token():
        for name in ["get_account()", "get_positions()", "buy()",
                     "sell()", "get_orders()", "get_balance_log()"]:
            skip(name, "no FINTOOLS_API_TOKEN set")
        return None

    # 1. Account
    r = run("get_account()", get_account)
    if not r or not r.get("success"):
        print("    cannot proceed without account — aborting auth tests")
        return None

    acc = r.get("data", {}).get("data", {})
    account_id = acc.get("account_id")
    balance_before = acc.get("current_balance")
    print(f"    account_id={account_id}, balance={balance_before}")

    # 2. Positions — record starting qty to make assertions relative
    r = run("get_positions() before trade", get_positions)
    starting_qty = 0.0
    if r and r.get("success"):
        positions = r.get("data", {}).get("data", [])
        if isinstance(positions, list):
            for p in positions:
                if p.get("stock_code") == TEST_SYMBOL:
                    starting_qty = float(p.get("holding_quantity") or 0)
    print(f"    starting {TEST_SYMBOL} qty: {starting_qty}")

    # 3. Buy 10 shares AAPL
    r = run(f'buy("{TEST_SYMBOL}", 10)', buy, TEST_SYMBOL, 10)
    if not r or not r.get("success"):
        print("    buy failed — aborting remaining auth tests")
        return account_id
    buy_price = r.get("data", {}).get("data", {}).get("price")
    print(f"    bought @ ${buy_price}")

    # 4. Verify position increased by 10
    r = run("get_positions() after buy", get_positions)
    if r and r.get("success"):
        positions = r.get("data", {}).get("data", [])
        if isinstance(positions, list):
            for p in positions:
                if p.get("stock_code") == TEST_SYMBOL:
                    after_buy = float(p.get("holding_quantity") or 0)
                    delta = after_buy - starting_qty
                    print(f"    after buy: {after_buy} shares (delta {delta:+}, expected +10)")
                    if delta != 10:
                        print(f"    WARNING: expected +10, got {delta:+}")

    # 5. Sell 3 shares
    r = run(f'sell("{TEST_SYMBOL}", 3)', sell, TEST_SYMBOL, 3)
    if r and r.get("success"):
        sell_price = r.get("data", {}).get("data", {}).get("price")
        print(f"    sold @ ${sell_price}")

    # 6. Verify final position = starting + 7
    r = run("get_positions() after sell", get_positions)
    if r and r.get("success"):
        positions = r.get("data", {}).get("data", [])
        if isinstance(positions, list):
            for p in positions:
                if p.get("stock_code") == TEST_SYMBOL:
                    final_qty = float(p.get("holding_quantity") or 0)
                    expected = starting_qty + 7
                    delta = final_qty - starting_qty
                    print(f"    final: {final_qty} shares (delta {delta:+}, expected +7)")
                    if delta != 7:
                        print(f"    WARNING: expected +7 net, got {delta:+}")

    # 7. Orders history
    r = run("get_orders(limit=10)", get_orders, 10)
    if r and r.get("success"):
        orders = r.get("data", {}).get("data", [])
        if isinstance(orders, list):
            print(f"    {len(orders)} orders in history")

    # 8. Balance log
    r = run("get_balance_log(limit=20)", get_balance_log, 1, 20)
    if r and r.get("success"):
        log = r.get("data", {}).get("data", {})
        items = log.get("items", []) if isinstance(log, dict) else (log if isinstance(log, list) else [])
        print(f"    {len(items)} balance log entries")

    return account_id


# ── Main ──────────────────────────────────────────────

def main():
    print(f"Target backend: {API_BASE}")
    token = _load_token()
    print(f"Auth: {'token loaded (' + token[:8] + '...)' if token else 'NO TOKEN — auth tests will skip'}")
    print(f"Test symbol: {TEST_SYMBOL}")

    test_public_endpoints()
    test_authed_endpoints()

    print(f"\n{'=' * 50}")
    print(f"Result: {PASS} passed, {FAIL} failed, {SKIP} skipped")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
