"""FinMeta Simulation Trading Skill — A-Share + Crypto.

Usage:
    from finmeta_simulation_skill.ashare import buy, get_account
    from finmeta_simulation_skill.crypto import buy as crypto_buy, get_account as crypto_account

Or from the top-level:
    from finmeta_simulation_skill import ashare, crypto
    ashare.buy("600519.SH", 100)
    crypto.buy("BTC/USDT", 0.01)
"""

from . import ashare
from . import crypto

__all__ = ["ashare", "crypto"]
