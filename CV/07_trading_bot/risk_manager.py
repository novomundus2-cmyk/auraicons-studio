"""Institutional-grade risk management and capital preservation system."""

from __future__ import annotations

import time
from typing import Any

from .models import OrderSide, Position, PositionSide, RiskConfig, StrategySignal


class RiskManager:
    def __init__(self, config: RiskConfig | None = None) -> None:
        self.config = config or RiskConfig()
        self.daily_peak_equity_cents: int = 1_000_000  # 10,000.00 EUR initial
        self.daily_start_time: float = time.time()
        self.circuit_breaker_tripped: bool = False

    def check_circuit_breaker(self, current_equity_cents: int) -> bool:
        """Halts trading if drawdown from peak exceeds max_daily_drawdown_pct."""
        now = time.time()
        # Reset 24-hour window
        if now - self.daily_start_time > 86400:
            self.daily_peak_equity_cents = current_equity_cents
            self.daily_start_time = now
            self.circuit_breaker_tripped = False

        if current_equity_cents > self.daily_peak_equity_cents:
            self.daily_peak_equity_cents = current_equity_cents

        if self.daily_peak_equity_cents > 0:
            drawdown_pct = (
                (self.daily_peak_equity_cents - current_equity_cents)
                / self.daily_peak_equity_cents
            ) * 100.0

            if drawdown_pct >= self.config.max_daily_drawdown_pct:
                self.circuit_breaker_tripped = True
                return True

        return self.circuit_breaker_tripped

    def calculate_position_size(
        self,
        symbol: str,
        price: float,
        total_equity_cents: int,
        stop_loss_price: float | None = None,
    ) -> float:
        """Computes volatility & risk-adjusted position sizing."""
        if price <= 0 or total_equity_cents <= 0:
            return 0.0

        equity_eur = total_equity_cents / 100.0
        risk_budget_eur = equity_eur * (self.config.max_risk_per_trade_pct / 100.0)

        # Distance to stop loss
        if stop_loss_price and stop_loss_price > 0 and stop_loss_price < price:
            sl_distance = price - stop_loss_price
        else:
            sl_distance = price * (self.config.default_stop_loss_pct / 100.0)

        sl_distance = max(sl_distance, price * 0.005)  # minimum 0.5% buffer
        qty = risk_budget_eur / sl_distance

        # Cap single order size to max 25% of portfolio
        max_notional_eur = equity_eur * 0.25
        if qty * price > max_notional_eur:
            qty = max_notional_eur / price

        # Precision formatting
        if price > 1000:  # e.g. BTC
            return round(qty, 4)
        elif price > 50:
            return round(qty, 2)
        else:
            return round(qty, 1)

    def evaluate_position_exits(
        self,
        position: Position,
        current_price: float,
    ) -> tuple[bool, str, str]:
        """Checks Stop-Loss, Take-Profit, and Trailing Stop triggers.

        Returns: (should_exit, side, reason)
        """
        if position.quantity <= 0 or position.side != PositionSide.LONG:
            return False, "HOLD", ""

        # Update peak price for trailing stop
        if current_price > position.peak_price:
            position.peak_price = current_price

        # 1. Hard Stop-Loss Check
        if position.stop_loss_price and current_price <= position.stop_loss_price:
            return (
                True,
                "SELL",
                f"Stop-Loss ejecutado: precio actual {current_price:.2f} <= SL {position.stop_loss_price:.2f}",
            )

        # 2. Hard Take-Profit Check
        if position.take_profit_price and current_price >= position.take_profit_price:
            return (
                True,
                "SELL",
                f"Take-Profit alcanzado: precio actual {current_price:.2f} >= TP {position.take_profit_price:.2f}",
            )

        # 3. Trailing Stop Check
        if self.config.use_trailing_stop and position.average_entry_price > 0:
            gain_pct = (
                (position.peak_price - position.average_entry_price)
                / position.average_entry_price
            ) * 100.0

            if gain_pct >= self.config.trailing_stop_activation_pct:
                trail_stop = position.peak_price * (
                    1.0 - (self.config.trailing_stop_distance_pct / 100.0)
                )
                if current_price <= trail_stop:
                    return (
                        True,
                        "SELL",
                        f"Trailing Stop ejecutado: pico {position.peak_price:.2f}, retroceso a {current_price:.2f}",
                    )

        return False, "HOLD", ""

    def validate_liquidity_gatekeeper(
        self,
        symbol: str,
        spread_pct: float,
        max_allowed_spread_pct: float = 0.15,
    ) -> tuple[bool, str]:
        """
        Enforces execution strictly in liquid markets.
        Rejects orders if Bid-Ask spread exceeds 0.15% to avoid slippage and illiquid traps.
        """
        if spread_pct > max_allowed_spread_pct:
            return (
                False,
                f"RECHAZO POR ILIQUIDEZ: Spread {spread_pct:.3f}% supera el límite prudencial de {max_allowed_spread_pct:.2f}% en {symbol}.",
            )
        return (
            True,
            f"LIQUIDEZ APROBADA: Spread {spread_pct:.3f}% dentro del umbral Tier-1 (< {max_allowed_spread_pct:.2f}%).",
        )

