"""Base Strategy class for the Novus Trading Bot."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..models import Candle, MarketTick, StrategySignal, StrategyType


class BaseStrategy(ABC):
    def __init__(self, name: str, strategy_type: StrategyType) -> None:
        self.name = name
        self.strategy_type = strategy_type

    @abstractmethod
    def evaluate(
        self,
        symbol: str,
        candles: list[Candle],
        current_tick: MarketTick,
    ) -> StrategySignal:
        """Evaluates market state and returns a concrete BUY, SELL, or HOLD signal."""
        pass
