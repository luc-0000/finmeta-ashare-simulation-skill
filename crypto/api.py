#!/usr/bin/env python3
"""
Crypto simulation trading.

Used via the unified skill:
    from finmeta_simulation_skill.crypto import buy, get_account

Or CLI (from skill root):
    python crypto/api.py --action account
    python crypto/api.py --action buy --symbol BTC/USDT --quantity 0.01

Env vars: FINTOOLS_API_TOKEN
"""

import argparse, json, os, sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = SKILL_DIR / "config.json"
API_BASE = os.getenv("FINTOOLS_API_BASE", "https://fin-meta.net")
API_PREFIX = "/api/v1/crypto"


def _ensure_requests():
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


# ═══════════ Config ═══════════

def _load_config():
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except (json.JSONDecodeError, KeyError):
            return {}
    return {}


def _save_config(cfg: dict):
    CONFIG_FILE.write_text(json.dumps(cfg))


def _load_token():
    token = os.getenv("FINTOOLS_API_TOKEN") or os.getenv("GITEA_ACCESS_TOKEN")
    if token:
        return token
    return _load_config().get("token", "")


def _save_token(token):
    cfg = _load_config()
    cfg["token"] = token
    _save_config(cfg)


def _headers():
    return {"Authorization": f"Bearer {_load_token()}", "Content-Type": "application/json"}


def _url(path: str) -> str:
    return f"{API_BASE}{API_PREFIX}{path}"


def _get(path, params=None):
    try:
        r = requests.get(_url(path), headers=_headers(), params=params, timeout=60)
        r.raise_for_status()
        return {"success": True, "data": r.json()}
    except requests.exceptions.RequestException as e:
        return _handle_error(e)


def _post(path, body=None):
    try:
        r = requests.post(_url(path), headers=_headers(), json=body or {}, timeout=60)
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


def _require_token():
    token = _load_token()
    if not token:
        print(
            "Missing API token. Get yours from https://fin-meta.net/profile, then:\n"
            "  python crypto/api.py --token YOUR_TOKEN",
            file=sys.stderr,
        )
        sys.exit(1)
    return token


# ═══════════ 行情查询 (no auth) ═══════════

def list_symbols():
    """列出所有支持的加密货币交易对"""
    return _get("/symbols")


def get_quotes(symbols):
    """批量查询行情

    Args:
        symbols: 逗号分隔字符串或数组，如 "BTC/USDT,ETH/USDT"
    """
    if isinstance(symbols, str):
        symbols = [s.strip() for s in symbols.split(",")]
    return _get("/quotes", {"symbols": ",".join(symbols)})


def get_kline(symbol: str, limit: int = 100):
    """查询 K 线数据

    Args:
        symbol: 交易对，如 BTC/USDT
        limit: 返回 K 线根数，最大 500
    """
    return _get("/kline", {"symbol": symbol, "limit": min(limit, 500)})


# ═══════════ 账户查询 ═══════════

def get_account():
    """获取账户概览（余额、总市值、P/L 等）"""
    _require_token()
    return _get("/account")


# ═══════════ 交易操作 ═══════════

def buy(symbol: str, quantity: float):
    """买入加密货币

    Args:
        symbol: 交易对，如 BTC/USDT
        quantity: 买入数量（币本位，如 0.01 BTC）
    """
    _require_token()
    return _post("/orders/buy", {"symbol": symbol, "quantity": quantity})


def sell(symbol: str, quantity: float):
    """卖出加密货币

    Args:
        symbol: 交易对，如 BTC/USDT
        quantity: 卖出数量（币本位，如 0.01 BTC）
    """
    _require_token()
    return _post("/orders/sell", {"symbol": symbol, "quantity": quantity})


# ═══════════ 历史记录 ═══════════

def get_orders(limit: int = 20):
    """查询历史订单"""
    _require_token()
    return _get("/orders", {"limit": min(limit, 100)})


# ═══════════ CLI ═══════════

def main():
    parser = argparse.ArgumentParser(description="Crypto simulation trading CLI")
    parser.add_argument("--action", required=False, default="")
    parser.add_argument("--symbol")
    parser.add_argument("--symbols")
    parser.add_argument("--quantity", type=float)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--token", help="Save API token to config.json")
    args = parser.parse_args()

    if args.token:
        _save_token(args.token)
        print("Token saved to", CONFIG_FILE)
        if not args.action:
            return

    if not args.action:
        parser.print_help()
        sys.exit(0)

    AUTH_ACTIONS = {"account", "buy", "sell", "orders"}

    if args.action in AUTH_ACTIONS:
        _require_token()

    if args.action == "list_symbols":
        result = list_symbols()
    elif args.action == "get_quotes":
        result = get_quotes(args.symbols) if args.symbols else {"success": False, "error": "missing --symbols"}
    elif args.action == "kline":
        result = get_kline(args.symbol, args.limit) if args.symbol else {"success": False, "error": "missing --symbol"}
    elif args.action == "account":
        result = get_account()
    elif args.action == "buy":
        result = buy(args.symbol, args.quantity) if args.symbol and args.quantity else {"success": False, "error": "missing --symbol or --quantity"}
    elif args.action == "sell":
        result = sell(args.symbol, args.quantity) if args.symbol and args.quantity else {"success": False, "error": "missing --symbol or --quantity"}
    elif args.action == "orders":
        result = get_orders(args.limit)
    else:
        result = {"success": False, "error": f"unknown action: {args.action}"}

    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result and result.get("success") else 1)


if __name__ == "__main__":
    main()
