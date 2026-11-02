"""Data models and domain schemas for the Novus Trading Bot."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import time
from typing import Any


class StrategyType(str, Enum):
    VWAP_MEAN_REVERSION = "VWAP_MEAN_REVERSION"
    MOMENTUM_EMA_RSI = "MOMENTUM_EMA_RSI"
    DYNAMIC_GRID = "DYNAMIC_GRID"
    STATISTICAL_PAIRS = "STATISTICAL_PAIRS"
    TENSORFLOW_ADAPTIVE = "TENSORFLOW_ADAPTIVE"
    TRADING_BUSINESS_SCHOOL = "TRADING_BUSINESS_SCHOOL"


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    TAKE_PROFIT = "TAKE_PROFIT"


class PositionSide(str, Enum):
    FLAT = "FLAT"
    LONG = "LONG"
    SHORT = "SHORT"


@dataclass
class Candle:
    timestamp: float
    open: float
    high: float
    low: float
    close: float
    volume: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
        }


@dataclass
class MarketTick:
    symbol: str
    price: float
    volume: float
    timestamp: float
    vwap: float
    z_score: float
    volatility_mad: float
    signal: str  # 'BUY', 'SELL', 'HOLD'
    confidence_pct: float
    bid: float = 0.0
    ask: float = 0.0

    def __post_init__(self) -> None:
        if self.bid == 0.0:
            self.bid = round(self.price * 0.9998, 5)
        if self.ask == 0.0:
            self.ask = round(self.price * 1.0002, 5)


@dataclass
class TradeRationale:
    thesis: str = "Reversión a la Media Cuantitativa"
    trigger: str = "Desviación estadística Z-score < -1.8"
    factors: list[str] = field(default_factory=list)
    risk_reward_ratio: float = 2.2
    stop_loss_justification: str = "Ajustado a 1.5 ATR bajo soporte de volatilidad"
    take_profit_justification: str = "Objetivo de convergencia al VWAP ponderado"
    historical_edge: str = "78.4% de efectividad en las últimas 120 sesiones"
    orderbook_bias: str = "Presión de compra en niveles clave de liquidez"

    def to_dict(self) -> dict[str, Any]:
        return {
            "thesis": self.thesis,
            "trigger": self.trigger,
            "factors": self.factors,
            "risk_reward_ratio": self.risk_reward_ratio,
            "stop_loss_justification": self.stop_loss_justification,
            "take_profit_justification": self.take_profit_justification,
            "historical_edge": self.historical_edge,
            "orderbook_bias": self.orderbook_bias,
        }


@dataclass
class StrategySignal:
    symbol: str
    action: str  # 'BUY', 'SELL', 'HOLD'
    confidence: float
    reason: str
    target_price: float
    stop_loss: float | None = None
    take_profit: float | None = None
    strategy: StrategyType = StrategyType.VWAP_MEAN_REVERSION
    metadata: dict[str, Any] = field(default_factory=dict)
    rationale: TradeRationale | None = None


@dataclass
class Order:
    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: float | None = None
    status: str = "PENDING"  # PENDING, FILLED, REJECTED, CANCELLED
    created_at: float = field(default_factory=time.time)
    filled_at: float | None = None
    filled_price: float | None = None
    commission_cents: int = 0


@dataclass
class Position:
    symbol: str
    side: PositionSide = PositionSide.FLAT
    quantity: float = 0.0
    average_entry_price: float = 0.0
    current_price: float = 0.0
    unrealized_pnl_cents: int = 0
    realized_pnl_cents: int = 0
    stop_loss_price: float | None = None
    take_profit_price: float | None = None
    peak_price: float = 0.0
    opened_at: float = 0.0
    updated_at: float = 0.0


@dataclass
class ExecutedTrade:
    trade_id: str
    correlation_id: str
    idempotency_key: str
    symbol: str
    side: str  # 'BUY', 'SELL'
    price: float
    qty: float
    amount_cents: int
    pnl_cents: int
    status: str
    timestamp: float
    block_hash: str
    strategy_used: str = "VWAP_MEAN_REVERSION"
    execution_fee_cents: int = 0
    rationale: dict[str, Any] = field(default_factory=dict)


@dataclass
class RiskConfig:
    max_risk_per_trade_pct: float = 2.0  # 2% of total equity
    default_stop_loss_pct: float = 1.5  # 1.5% below entry
    default_take_profit_pct: float = 3.5  # 3.5% above entry
    use_trailing_stop: bool = True
    trailing_stop_activation_pct: float = 1.5
    trailing_stop_distance_pct: float = 1.0
    max_daily_drawdown_pct: float = 5.0  # Circuit breaker threshold
    max_open_positions: int = 4
    slippage_bps: float = 2.0  # 2 basis points
    commission_bps: float = 5.0  # 5 basis points


@dataclass
class BacktestReport:
    symbol: str
    strategy: str
    start_date: str
    end_date: str
    initial_capital_eur: float
    final_equity_eur: float
    total_return_pct: float
    annualized_return_pct: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown_pct: float
    win_rate_pct: float
    profit_factor: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    equity_curve: list[dict[str, Any]]
    trades: list[dict[str, Any]]
    completed_trades: list[dict[str, Any]] = field(default_factory=list)
    post_mortem_summary: dict[str, Any] = field(default_factory=dict)
