#!/usr/bin/env python3
"""
A-Share simulation trading skill (v3 — per-account routing).

Two entry points share the same business logic (SSOT):

1. Python import (for LLM tool-calling agents):

    from skills.finmeta_ashare_simulation_skill import (
        list_selectable_stocks, buy_stock, get_account_snapshot,
    )

2. CLI:

    python trading_api.py --action account
    python trading_api.py --action buy --stock-code 600519.SH --quantity 100

Setup: set FINTOOLS_API_TOKEN + FINTOOLS_SIMULATION_ACCOUNT_ID env vars
       (from Profile page + My Simulation page).
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


def _load_account_id():
    """Read simulation_account_id from env var or config.json."""
    val = os.getenv("FINTOOLS_SIMULATION_ACCOUNT_ID")
    if val:
        try:
            return int(val)
        except ValueError:
            pass
    return _load_config().get("account_id")


def _save_account_id(account_id: int):
    cfg = _load_config()
    cfg["account_id"] = account_id
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


def _require_account_id():
    """Raise SystemExit if no account_id configured."""
    aid = _load_account_id()
    if not aid:
        print(
            "Missing simulation account ID.\n"
            "Get yours from https://fin-meta.net/my/simulation, then:\n"
            "  python trading_api.py --account-id YOUR_ACCOUNT_ID\n"
            "Or set env var: export FINTOOLS_SIMULATION_ACCOUNT_ID=YOUR_ID",
            file=sys.stderr,
        )
        sys.exit(1)
    return aid


# ═══════════ 行情查询 (no account required) ═══════════

def list_selectable_stocks():
    """查询可选股票列表及最新行情"""
    return _get("/stocks")


def get_quote_by_symbols(symbols):
    """批量查询指定股票代码的最新行情

    Args:
        symbols: 股票代码数组或逗号分隔的字符串，如 "600519.SH" 或 ["600519.SH", "000001.SZ"]
    """
    if isinstance(symbols, str):
        symbols = [s.strip() for s in symbols.split(",")]
    return _get("/stocks/quotes", {"symbols": ",".join(symbols)})


_PERIOD_ALIASES = {"day": "1d", "daily": "1d", "1d": "1d"}


def get_stock_kline(stock_code: str, period: str = "1d", limit: int = 60):
    """查询指定股票的K线走势数据

    Args:
        stock_code: 股票代码，如 600519.SH
        period: 周期，'1d' / 'day' / 'daily' 都接受，normalize 到 backend 要求的 '1d'
        limit: 返回K线根数，最大 200
    """
    period = _PERIOD_ALIASES.get(period, period)
    return _get(f"/stocks/{stock_code}/kline", {"period": period, "limit": min(limit, 200)})


# ═══════════ 账户查询 (require account_id) ═══════════

def get_account_snapshot(account_id: int = None):
    """获取单个账户详情（余额、总市值、总资产等）"""
    aid = account_id or _require_account_id()
    return _get(f"/accounts/{aid}")


def get_positions(account_id: int = None):
    """查询当前持仓列表及浮动盈亏"""
    aid = account_id or _require_account_id()
    return _get(f"/accounts/{aid}/positions")


# ═══════════ 交易操作 (require account_id) ═══════════

def buy_stock(stock_code: str, quantity: int, account_id: int = None):
    """买入股票

    Args:
        stock_code: 股票代码，如 600519.SH
        quantity: 买入数量（股），必须 100 的整数倍
        account_id: 模拟账户 ID（可选，不传则用全局配置）
    """
    aid = account_id or _require_account_id()
    return _post(f"/accounts/{aid}/orders/buy", {"stock_code": stock_code, "quantity": quantity})


def sell_stock(stock_code: str, quantity: int, account_id: int = None):
    """卖出股票

    Args:
        stock_code: 股票代码，如 600519.SH
        quantity: 卖出数量（股），必须 100 的整数倍
        account_id: 模拟账户 ID（可选，不传则用全局配置）
    """
    aid = account_id or _require_account_id()
    return _post(f"/accounts/{aid}/orders/sell", {"stock_code": stock_code, "quantity": quantity})


# ═══════════ 历史记录 (require account_id) ═══════════

def get_orders_history(limit: int = 50, account_id: int = None):
    """查询所有历史订单"""
    aid = account_id or _require_account_id()
    return _get(f"/accounts/{aid}/orders", {"limit": min(limit, 200)})


def get_buy_list(page: int = 1, limit: int = 50, account_id: int = None):
    """查询买入订单（分页）"""
    aid = account_id or _require_account_id()
    return _get(f"/accounts/{aid}/orders", {"page": page, "limit": min(limit, 200), "side": "buy"})


def get_sell_list(page: int = 1, limit: int = 50, account_id: int = None):
    """查询卖出订单（分页）"""
    aid = account_id or _require_account_id()
    return _get(f"/accounts/{aid}/orders", {"page": page, "limit": min(limit, 200), "side": "sell"})


def get_balance_log(page: int = 1, limit: int = 50, account_id: int = None):
    """查询资金流水（分页）"""
    aid = account_id or _require_account_id()
    return _get(f"/accounts/{aid}/balance-log", {"page": page, "limit": min(limit, 200)})


def get_fee_log(page: int = 1, limit: int = 50, account_id: int = None):
    """查询手续费流水（只含 buy/sell 类型）"""
    aid = account_id or _require_account_id()
    raw = _get(f"/accounts/{aid}/balance-log", {"page": page, "limit": min(limit, 200)})
    if raw.get("success") and raw["data"].get("data"):
        items = raw["data"]["data"].get("items", [])
        raw["data"]["items"] = [x for x in items if x.get("reason") in ("buy", "sell")]
    return raw


# ═══════════ 交易规则 (no account required) ═══════════

def get_trading_rules():
    """查询交易规则（费率、涨跌停、手数等）"""
    return _get("/rules")


# ═══════════ CLI 入口（SSOT：分派到上述函数） ═══════════

def main():
    parser = argparse.ArgumentParser(
        description="A-Share simulation trading CLI (v3 — per-account)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Setup:
  export FINTOOLS_API_TOKEN="your-token"              # from https://fin-meta.net/profile
  export FINTOOLS_SIMULATION_ACCOUNT_ID=123           # from https://fin-meta.net/my/simulation
  python trading_api.py --action account               # verify it works

  Or one-time save:
  python trading_api.py --token YOUR_TOKEN --account-id 123

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
    parser.add_argument("--token", help="Set API token and save to config.json")
    parser.add_argument("--account-id", type=int, help="Set simulation account ID and save to config.json")
    args = parser.parse_args()

    # One-time config save
    if args.token or args.account_id:
        if args.token:
            _save_token(args.token)
            print("Token saved to", CONFIG_FILE)
        if args.account_id:
            _save_account_id(args.account_id)
            print(f"Account ID {args.account_id} saved to {CONFIG_FILE}")
        if not args.action:
            return

    if not args.action:
        parser.print_help()
        sys.exit(0)

    NO_ACCOUNT_ACTIONS = {"list_stocks", "get_quote", "kline", "rules"}
    AUTH_ACTIONS = {"account", "positions", "buy", "sell", "orders_history",
                    "buy_list", "sell_list", "balance_log", "fee_log"}

    if not _load_token() and args.action in AUTH_ACTIONS:
        print("Missing API token. Get yours from https://fin-meta.net/profile, then:", file=sys.stderr)
        print("  python trading_api.py --token YOUR_TOKEN_HERE", file=sys.stderr)
        sys.exit(1)

    if args.action in AUTH_ACTIONS and args.action not in NO_ACCOUNT_ACTIONS:
        _require_account_id()

    if args.action == "list_stocks":
        result = list_selectable_stocks()
    elif args.action == "get_quote":
        if not args.symbols:
            result = {"success": False, "error": "missing --symbols"}
        else:
            result = get_quote_by_symbols(args.symbols)
    elif args.action == "kline":
        if not args.stock_code:
            result = {"success": False, "error": "missing --stock-code"}
        else:
            result = get_stock_kline(args.stock_code, args.period, args.limit)
    elif args.action == "account":
        result = get_account_snapshot()
    elif args.action == "positions":
        result = get_positions()
    elif args.action == "buy":
        if not args.stock_code or not args.quantity:
            result = {"success": False, "error": "missing --stock-code or --quantity"}
        else:
            result = buy_stock(args.stock_code, args.quantity)
    elif args.action == "sell":
        if not args.stock_code or not args.quantity:
            result = {"success": False, "error": "missing --stock-code or --quantity"}
        else:
            result = sell_stock(args.stock_code, args.quantity)
    elif args.action == "orders_history":
        result = get_orders_history(args.limit)
    elif args.action == "buy_list":
        result = get_buy_list(args.page, args.limit)
    elif args.action == "sell_list":
        result = get_sell_list(args.page, args.limit)
    elif args.action == "balance_log":
        result = get_balance_log(args.page, args.limit)
    elif args.action == "fee_log":
        result = get_fee_log(args.page, args.limit)
    elif args.action == "rules":
        result = get_trading_rules()
    else:
        result = {"success": False, "error": f"unknown action: {args.action}"}

    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result and result.get("success") else 1)


if __name__ == "__main__":
    main()
