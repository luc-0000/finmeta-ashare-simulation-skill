#!/usr/bin/env python3
"""
A-Share simulation trading CLI. Calls Fintools Backend API.
One-step setup: set FINTOOLS_API_TOKEN (from Profile page) and you're done.
"""

import argparse, json, os, sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent
CONFIG_FILE = SKILL_DIR / "config.json"
API_BASE = os.getenv("FINTOOLS_API_BASE", "https://fin-meta.net")
API_PREFIX = "/api/v1/ashare"


def _ensure_requests():
    """Auto-install requests if not available."""
    try:
        import requests  # noqa: F811
        return requests
    except ImportError:
        import subprocess
        print("Installing requests...", file=sys.stderr)
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "requests", "-q"],
            stdout=sys.stderr, stderr=sys.stderr,
        )
        import requests  # noqa: F811
        return requests


requests = _ensure_requests()


def _load_token():
    token = os.getenv("FINTOOLS_API_TOKEN") or os.getenv("GITEA_ACCESS_TOKEN")
    if token:
        return token
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text()).get("token", "")
        except (json.JSONDecodeError, KeyError):
            return ""
    return ""


def _save_token(token):
    CONFIG_FILE.write_text(json.dumps({"token": token}))


def _headers():
    return {"Authorization": f"Bearer {_load_token()}", "Content-Type": "application/json"}


def _get(path, params=None):
    try:
        r = requests.get(f"{API_BASE}{API_PREFIX}{path}", headers=_headers(), params=params, timeout=60)
        r.raise_for_status()
        return {"success": True, "data": r.json()}
    except requests.exceptions.RequestException as e:
        return _handle_error(e)


def _post(path, body=None):
    try:
        r = requests.post(f"{API_BASE}{API_PREFIX}{path}", headers=_headers(), json=body or {}, timeout=60)
        r.raise_for_status()
        return {"success": True, "data": r.json()}
    except requests.exceptions.RequestException as e:
        return _handle_error(e)


def _handle_error(e):
    resp = getattr(e, "response", None)
    if resp is not None:
        try:
            detail = resp.json().get("detail", "")
            if detail:
                return {"success": False, "error": detail}
        except Exception:
            pass
        return {"success": False, "error": f"HTTP {resp.status_code}"}
    return {"success": False, "error": type(e).__name__}


def main():
    parser = argparse.ArgumentParser(
        description="A-Share simulation trading CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Setup:
  export FINTOOLS_API_TOKEN="your-token"   # from https://fin-meta.net/profile
  python trading_api.py --action account   # verify it works

Examples:
  Market:  --action list_stocks | get_quote --symbols "600519.SH" | kline --stock-code 600519.SH
  Account: --action account | positions
  Trading: --action buy|sell --stock-code 600519.SH --quantity 100
  History: --action orders_history | buy_list | sell_list | balance_log | fee_log
        """,
    )
    parser.add_argument("--action", required=False, default="")
    parser.add_argument("--stock-code")
    parser.add_argument("--symbols")
    parser.add_argument("--quantity", type=int)
    parser.add_argument("--period", default="1d", choices=["1d"])
    parser.add_argument("--limit", type=int, default=60)
    parser.add_argument("--page", type=int, default=1)
    parser.add_argument("--token", help="Set token and save to config.json (one-time setup)")
    args = parser.parse_args()

    if args.token:
        _save_token(args.token)
        print("Token saved to", CONFIG_FILE)
        return

    if not args.action:
        parser.print_help()
        sys.exit(0)

    if not _load_token():
        print("Missing API token. Get yours from https://fin-meta.net/profile, then:", file=sys.stderr)
        print("  python trading_api.py --token YOUR_TOKEN_HERE", file=sys.stderr)
        sys.exit(1)

    result = None

    if args.action == "list_stocks":
        result = _get("/stocks")
    elif args.action == "get_quote":
        if not args.symbols:
            result = {"success": False, "error": "missing --symbols"}
        else:
            result = _get("/stocks/quotes", {"symbols": args.symbols})
    elif args.action == "kline":
        if not args.stock_code:
            result = {"success": False, "error": "missing --stock-code"}
        else:
            result = _get(f"/stocks/{args.stock_code}/kline", {"period": args.period, "limit": args.limit})
    elif args.action == "account":
        result = _get("/account")
    elif args.action == "positions":
        result = _get("/positions")
    elif args.action == "buy":
        if not args.stock_code or not args.quantity:
            result = {"success": False, "error": "missing --stock-code or --quantity"}
        else:
            result = _post("/orders/buy", {"stock_code": args.stock_code, "quantity": args.quantity})
    elif args.action == "sell":
        if not args.stock_code or not args.quantity:
            result = {"success": False, "error": "missing --stock-code or --quantity"}
        else:
            result = _post("/orders/sell", {"stock_code": args.stock_code, "quantity": args.quantity})
    elif args.action == "orders_history":
        result = _get("/orders", {"limit": min(args.limit, 200)})
    elif args.action == "buy_list":
        result = _get("/orders/buy", {"page": args.page, "limit": min(args.limit, 200)})
    elif args.action == "sell_list":
        result = _get("/orders/sell", {"page": args.page, "limit": min(args.limit, 200)})
    elif args.action == "balance_log":
        result = _get("/balance-log", {"page": args.page, "limit": min(args.limit, 200)})
    elif args.action == "fee_log":
        raw = _get("/balance-log", {"page": args.page, "limit": min(args.limit, 200)})
        if raw.get("success") and raw["data"].get("data"):
            items = raw["data"]["data"].get("items", [])
            raw["data"]["items"] = [x for x in items if x.get("reason") in ("buy", "sell")]
        result = raw
    elif args.action == "rules":
        result = _get("/rules")

    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result and result.get("success") else 1)


if __name__ == "__main__":
    main()
