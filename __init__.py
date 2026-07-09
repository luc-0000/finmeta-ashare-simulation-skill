"""A股模拟交易 Skill — 调用 Fintools Backend API

用户代码这样用：

    from finmeta_ashare_simulation_skill import buy_stock, get_account_snapshot

平台在 Pod 启动时注入 FINTOOLS_API_TOKEN 环境变量。
注意：包目录名 finmeta-ashare-simulation-skill 含 dash，不是合法 Python 模块名。
若用 import，需要把目录重命名为 finmeta_ashare_simulation_skill（或别名 ashare_simulation），
或者用 importlib：
    import importlib
    skill = importlib.import_module("finmeta-ashare-simulation-skill")
"""

from .trading_api import (
    list_selectable_stocks,
    get_quote_by_symbols,
    get_stock_kline,
    get_account_snapshot,
    get_positions,
    buy_stock,
    sell_stock,
    get_orders_history,
    get_buy_list,
    get_sell_list,
    get_balance_log,
    get_fee_log,
    get_trading_rules,
    main,
)

__all__ = [
    "list_selectable_stocks",
    "get_quote_by_symbols",
    "get_stock_kline",
    "get_account_snapshot",
    "get_positions",
    "buy_stock",
    "sell_stock",
    "get_orders_history",
    "get_buy_list",
    "get_sell_list",
    "get_balance_log",
    "get_fee_log",
    "get_trading_rules",
    "main",
]
