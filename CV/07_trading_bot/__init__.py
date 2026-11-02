"""NovusMundus · Quantitative Algorithmic Trading Bot System (v3.0 Enterprise)

Production-grade algorithmic trading core featuring:
- Multiple quantitative strategies (VWAP Mean Reversion, EMA+RSI Momentum, Dynamic Grid, Pairs Arbitrage).
- Vectorized technical indicators (VWAP, MAD, Bollinger, EMA, RSI, ATR, MACD).
- Dynamic institutional risk management (Kelly/fractional sizing, ATR trailing stops, daily drawdown circuit breaker).
- Event-driven backtester with full performance metrics (Sharpe, Sortino, Max Drawdown, Profit Factor).
- Dual settlement: In-memory order execution + PostgreSQL 17 double-entry ledger with SHA-256 block chain.
- Autonomous Autopilot daemon and REST/CLI interfaces.
"""

from .models import (
    Candle,
    ExecutedTrade,
    MarketTick,
    Order,
    Position,
    RiskConfig,
    StrategySignal,
    StrategyType,
)
from .bot_core import QuantitativeTradingBot, GLOBAL_QUANT_BOT

__all__ = [
    "Candle",
    "MarketTick",
    "Order",
    "Position",
    "ExecutedTrade",
    "RiskConfig",
    "StrategySignal",
    "StrategyType",
    "QuantitativeTradingBot",
    "GLOBAL_QUANT_BOT",
]
