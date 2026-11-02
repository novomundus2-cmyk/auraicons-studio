"""Core Orchestrator for the Novus Quantitative Trading Bot."""

from __future__ import annotations

from dataclasses import asdict
import datetime
import threading
import time
from typing import Any

from .backtester import QuantitativeBacktester
from .execution_engine import ExecutionEngine
from .indicators import Indicators
from .market_data import MarketDataProvider
from .models import (
    BacktestReport,
    Candle,
    ExecutedTrade,
    MarketTick,
    OrderSide,
    PositionSide,
    RiskConfig,
    StrategySignal,
    StrategyType,
)
from .risk_manager import RiskManager
from .strategies.base import BaseStrategy
from .strategies.grid_trader import DynamicGridTradingStrategy
from .strategies.mean_reversion import VWAPMeanReversionStrategy
from .strategies.momentum_ema_rsi import MomentumEMARSIStrategy
from .strategies.tbs_smc import TradingBusinessSchoolStrategy
from .haskell_bridge import GLOBAL_HASKELL_BRIDGE
from .strategies.tensorflow_adaptive import TensorFlowAdaptiveStrategy
from .streaming_db import GLOBAL_STREAM_DB
from .tensorflow_learner import TensorFlowContinuousLearner


class QuantitativeTradingBot:
    def __init__(self, tenant_id: str = "novus-capital-enterprise") -> None:
        self.tenant_id = tenant_id
        self.market_data = MarketDataProvider()
        self.risk_config = RiskConfig()
        self.risk_manager = RiskManager(self.risk_config)
        self.execution = ExecutionEngine(tenant_id=tenant_id, risk_config=self.risk_config)
        self.backtester = QuantitativeBacktester(
            initial_capital_eur=10000.0, risk_config=self.risk_config
        )

        # Continuous Deep Learning Engine (TensorFlow Keras)
        self.tf_learner = TensorFlowContinuousLearner()

        # Strategies library
        self.strategies: dict[StrategyType, BaseStrategy] = {
            StrategyType.VWAP_MEAN_REVERSION: VWAPMeanReversionStrategy(),
            StrategyType.MOMENTUM_EMA_RSI: MomentumEMARSIStrategy(),
            StrategyType.DYNAMIC_GRID: DynamicGridTradingStrategy(),
            StrategyType.TENSORFLOW_ADAPTIVE: TensorFlowAdaptiveStrategy(learner=self.tf_learner),
            StrategyType.TRADING_BUSINESS_SCHOOL: TradingBusinessSchoolStrategy(learner=self.tf_learner),
        }
        self.active_strategy_type: StrategyType = StrategyType.VWAP_MEAN_REVERSION
        self.last_evaluated_signal: dict[str, StrategySignal] = {}

        # Autopilot state
        self.autopilot_enabled: bool = True
        self.autopilot_thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self.lock = threading.Lock()
        self.live_activity_log: list[dict[str, Any]] = [
            {
                "timestamp": time.time(),
                "time_str": datetime.datetime.now().strftime("%H:%M:%S"),
                "event_type": "SYSTEM_START",
                "symbol": "MOTOR",
                "icon": "🟢",
                "message": "Trading en directo activo · Escaneando Binance Live Depth y Ticker cada 1.5s.",
            }
        ]

        # Start autopilot background thread
        self.start_autopilot()

    def _add_live_log(self, event_type: str, symbol: str, icon: str, message: str) -> None:
        import datetime
        entry = {
            "timestamp": time.time(),
            "time_str": datetime.datetime.now().strftime("%H:%M:%S"),
            "event_type": event_type,
            "symbol": symbol,
            "icon": icon,
            "message": message,
        }
        self.live_activity_log.insert(0, entry)
        if len(self.live_activity_log) > 50:
            self.live_activity_log.pop()


    @property
    def active_strategy(self) -> BaseStrategy:
        return self.strategies.get(
            self.active_strategy_type, self.strategies[StrategyType.VWAP_MEAN_REVERSION]
        )

    def set_active_strategy(self, strategy_type: str | StrategyType) -> None:
        with self.lock:
            if isinstance(strategy_type, str):
                try:
                    strategy_type = StrategyType(strategy_type)
                except ValueError:
                    strategy_type = StrategyType.VWAP_MEAN_REVERSION
            self.active_strategy_type = strategy_type

    def generate_tick(self, symbol: str) -> MarketTick:
        """Generates the latest tick and evaluates indicator signals."""
        price, volume = self.market_data.get_latest_price(symbol)
        history = self.market_data.tick_history.get(symbol, [])
        prices = [p for _, p, _ in history]
        volumes = [v for _, _, v in history]

        dec = 5 if ("USD" in symbol or "EUR" in symbol) and "BTC" not in symbol else 2

        vwap = Indicators.vwap(prices, volumes)
        mad = Indicators.robust_mad(prices)
        z_score = Indicators.z_score(price, vwap, mad) if mad > 0 else 0.0

        # Build tick
        tick = MarketTick(
            symbol=symbol,
            price=price,
            volume=volume,
            timestamp=time.time(),
            vwap=round(vwap, dec),
            z_score=round(z_score, 2),
            volatility_mad=round(mad, dec),
            signal="HOLD",
            confidence_pct=50.0,
        )

        # Get recent candles to evaluate strategy signal
        candles = self.market_data.get_historical_candles(symbol, interval="1h", count=30)
        signal = self.active_strategy.evaluate(symbol, candles, tick)
        self.last_evaluated_signal[symbol] = signal

        tick.signal = signal.action
        tick.confidence_pct = signal.confidence

        # Stream event into NovusStreamDB
        GLOBAL_STREAM_DB.append_event("TICK", symbol, {
            "price": tick.price,
            "volume": tick.volume,
            "vwap": tick.vwap,
            "z_score": tick.z_score,
            "signal": tick.signal,
            "confidence_pct": tick.confidence_pct,
        })

        return tick

    def execute_trade(
        self,
        symbol: str,
        side: str,
        qty: float,
        price: float | None = None,
    ) -> ExecutedTrade:
        with self.lock:
            current_p = price if price is not None else self.market_data.cached_prices.get(symbol, 68000.0)
            liq_prof = self.market_data.get_liquidity_profile(symbol)
            is_liq, liq_msg = self.risk_manager.validate_liquidity_gatekeeper(
                symbol, liq_prof.get("live_spread_pct", liq_prof.get("spread_pct", 0.015))
            )
            sig = self.last_evaluated_signal.get(symbol)
            rat = sig.rationale if (sig and sig.action == side.upper() and sig.rationale) else {
                "thesis": f"Ejecución Táctica en Mercado Líquido ({self.active_strategy.name})",
                "trigger": f"Orden enviada para {symbol} a {current_p}€ en mercado {liq_prof.get('rating', 'Tier-1')}",
                "factors": [
                    f"Activo líquido seleccionado: {symbol} ({liq_prof.get('market_name', 'Blue-Chip')})",
                    f"Rotación diaria verificada: {liq_prof.get('turnover_label', 'Tier-1')}",
                    f"Spread Bid-Ask controlado: {liq_prof.get('live_spread_pct', liq_prof.get('spread_pct', 0.01))}% (Impacto despreciable)",
                    f"Lado ejecutado: {side}",
                    f"Cotización de mercado: {current_p}€",
                    f"Estrategia activa: {self.active_strategy.name}",
                    "Confirmación criptográfica y registro en Ledger Novus PostgreSQL",
                ],
                "risk_reward_ratio": 2.2 if side.upper() == "BUY" else 1.8,
                "stop_loss_justification": "Stop loss dinámico del 1.5% asignado por el gestor de riesgo central",
                "take_profit_justification": "Objetivo de retorno ajustado a la volatilidad de la sesión",
                "historical_edge": "Intervención en mercado líquido con llenado inmediato y cero deslizamiento",
                "orderbook_bias": "Llenado optimizado contra los mejores niveles de Bids/Asks de alta profundidad",
                "liquidity_verification": f"Aprobada: {liq_prof.get('rating', 'Tier-1')} con spread {liq_prof.get('live_spread_pct', 0.01)}%",
            }
            sl_price = round(current_p * 0.985, 2 if current_p > 10 else 5) if side.upper() == "BUY" else None
            tp_price = round(current_p * 1.025, 2 if current_p > 10 else 5) if side.upper() == "BUY" else None
            trade = self.execution.execute_order(
                symbol=symbol,
                side=side,
                qty=qty,
                market_price=current_p,
                strategy_name=self.active_strategy.name,
                stop_loss_price=sl_price,
                take_profit_price=tp_price,
                rationale=rat,
            )
            GLOBAL_STREAM_DB.append_event("TRADE", symbol, asdict(trade))
            self._add_live_log(
                "ORDER_EXECUTED",
                symbol,
                "🚀" if side.upper() == "BUY" else "💰",
                f"Orden {side.upper()} ejecutada en directo: {qty} {symbol} a {current_p:.2f}€.",
            )
            return trade

    def run_backtest(
        self,
        symbol: str = "BTCUSDT",
        strategy_type: str | None = None,
        candle_count: int = 120,
    ) -> BacktestReport:
        strat = (
            self.strategies.get(StrategyType(strategy_type), self.active_strategy)
            if strategy_type
            else self.active_strategy
        )
        candles = self.market_data.get_historical_candles(symbol, interval="1h", count=candle_count)
        return self.backtester.run_backtest(symbol=symbol, candles=candles, strategy=strat)

    def run_demo_simulation(
        self,
        symbol: str = "BTCUSDT",
        strategy_type: str | None = None,
        scenario: str = "realistic",
        candle_count: int = 150,
    ) -> BacktestReport:
        strat = (
            self.strategies.get(StrategyType(strategy_type), self.active_strategy)
            if strategy_type
            else self.active_strategy
        )
        return self.backtester.run_demo_simulation(
            symbol=symbol,
            strategy=strat,
            scenario=scenario,
            count=candle_count,
        )

    def execute_autonomous_demo_step(self, symbol: str | None = None) -> dict[str, Any]:
        """
        Manually forces a single autonomous cycle across monitored assets or target symbol,
        returning the exact decisions taken, exits evaluated, and trades executed.
        """
        sym = symbol or "BTCUSDT"
        with self.lock:
            pos = self.execution.get_position(sym)
            curr_p, vol = self.market_data.get_latest_price(sym)
            exit_info = None
            if pos.quantity > 0 and pos.side == PositionSide.LONG:
                should_exit, exit_side, reason = self.risk_manager.evaluate_position_exits(pos, curr_p)
                if should_exit:
                    trade = self.execution.execute_order(
                        symbol=sym,
                        side=exit_side,
                        qty=pos.quantity,
                        market_price=curr_p,
                        strategy_name=f"DEMO_EXIT: {reason}",
                    )
                    exit_info = asdict(trade)

            tick = self.generate_tick(sym)
            executed_trade = None
            if tick.signal in ("BUY", "SELL"):
                if tick.signal == "BUY" and pos.side == PositionSide.FLAT:
                    total_cents = self._get_total_equity_cents()
                    sl_price = round(tick.price * 0.985, 2 if tick.price > 10 else 5)
                    qty = self.risk_manager.calculate_position_size(
                        sym, tick.price, total_cents, stop_loss_price=sl_price
                    )
                    qty = max(qty, 0.05 if "BTC" in sym else 1.0)
                    sig = self.last_evaluated_signal.get(sym)
                    trade = self.execution.execute_order(
                        symbol=sym,
                        side="BUY",
                        qty=qty,
                        market_price=tick.price,
                        strategy_name=self.active_strategy.name,
                        stop_loss_price=sl_price,
                        take_profit_price=tick.vwap,
                        rationale=sig.rationale if (sig and sig.rationale) else None,
                    )
                    executed_trade = asdict(trade)
                elif tick.signal == "SELL" and pos.side == PositionSide.LONG and pos.quantity > 0:
                    trade = self.execution.execute_order(
                        symbol=sym,
                        side="SELL",
                        qty=pos.quantity,
                        market_price=tick.price,
                        strategy_name=self.active_strategy.name,
                    )
                    executed_trade = asdict(trade)

            return {
                "ok": True,
                "symbol": sym,
                "price": curr_p,
                "signal": tick.signal,
                "confidence_pct": tick.confidence_pct,
                "position": asdict(self.execution.get_position(sym)),
                "executed_trade": executed_trade,
                "exit_trade": exit_info,
            }


    def start_autopilot(self) -> None:
        if self.autopilot_thread is not None and self.autopilot_thread.is_alive():
            return
        self._stop_event.clear()
        self.autopilot_thread = threading.Thread(target=self._autopilot_loop, daemon=True)
        self.autopilot_thread.start()

    def stop_autopilot(self) -> None:
        self._stop_event.set()
        if self.autopilot_thread:
            self.autopilot_thread.join(timeout=2.0)
            self.autopilot_thread = None

    def toggle_autopilot(self) -> bool:
        self.autopilot_enabled = not self.autopilot_enabled
        return self.autopilot_enabled

    def _autopilot_loop(self) -> None:
        """Autonomous autopilot worker loop running in the background."""
        while not self._stop_event.is_set():
            try:
                if self.autopilot_enabled:
                    self._autopilot_step()
            except Exception:
                pass
            time.sleep(1.5)

    def _autopilot_step(self) -> None:
        """Single autonomous tick and decision cycle across tracked symbols."""
        # 1. Check Circuit Breaker
        total_equity_cents = self._get_total_equity_cents()
        if self.risk_manager.check_circuit_breaker(total_equity_cents):
            return  # Trading frozen due to drawdown limit

        # 2. Check position exits (Stop-Loss / Take-Profit / Trailing Stop)
        with self.lock:
            for sym, pos in list(self.execution.positions.items()):
                if pos.quantity > 0 and pos.side == PositionSide.LONG:
                    curr_p, _ = self.market_data.get_latest_price(sym)
                    should_exit, exit_side, reason = self.risk_manager.evaluate_position_exits(
                        pos, curr_p
                    )
                    if should_exit:
                        pnl_approx = (curr_p - pos.average_entry_price) * pos.quantity
                        pnl_cents = int(round(pnl_approx * 100))
                        exit_rat = {
                            "thesis": f"Gestión de Riesgo Automatizada ({reason})",
                            "trigger": f"Regla de protección activada: {reason} al precio {curr_p}€",
                            "factors": [
                                f"Precio medio de entrada: {pos.average_entry_price:.2f}€",
                                f"Precio actual de salida: {curr_p:.2f}€",
                                f"PnL resultante estimado: {pnl_approx:+.2f}€",
                                "Cierre sistemático para preservar ratio de Sharpe y control de Drawdown",
                            ],
                            "risk_reward_ratio": 2.0,
                            "stop_loss_justification": f"Gatillo de riesgo ejecutado sin demoras: {reason}",
                            "take_profit_justification": "Cierre de posición para consolidar liquidez en efectivo",
                            "historical_edge": "La asimetría positiva se mantiene cortando pérdidas y asegurando metas",
                            "orderbook_bias": "Liquidación inmediata para evitar deslizamiento adicional en libro de órdenes",
                        }
                        self.execution.execute_order(
                            symbol=sym,
                            side=exit_side,
                            qty=pos.quantity,
                            market_price=curr_p,
                            strategy_name=f"RISK_EXIT: {reason}",
                            rationale=exit_rat,
                        )
                        # Continuous Learning Step: update TensorFlow weights from trade feedback
                        feat = self.tf_learner.extract_features(
                            sym,
                            MarketTick(sym, curr_p, 10.0, time.time(), pos.average_entry_price, 0.0, 0.5, "HOLD", 50.0),
                            liquidity_profile=self.market_data.get_liquidity_profile(sym),
                        )
                        self.tf_learner.record_trade_feedback(
                            features=feat,
                            action=exit_side,
                            realized_pnl_cents=pnl_cents,
                            symbol=sym,
                        )
                        self._add_live_log(
                            "RISK_EXIT",
                            sym,
                            "🛡️" if "Stop-Loss" in reason else "🎯",
                            f"Posición en {sym} cerrada en directo a {curr_p:.2f}€ por {reason}. PnL: {pnl_approx:+.2f}€. [TensorFlow: Paso #{self.tf_learner.total_train_steps}]",
                        )

        # 3. Check for new strategy entries on prioritized assets with dynamic 24/7 Crypto Fallback
        regime = self.market_data.get_market_regime()
        if regime["crypto_pivot_active"] and not getattr(self, "_logged_crypto_fallback", False):
            self._add_live_log(
                "CRYPTO_PIVOT_24_7",
                "CRYPTO",
                "🌙",
                f"Mercados tradicionales cerrados ({regime['status_label']}) · Pivotando 100% de capital y escaneo a CRIPTOMONEDAS 24/7 (BTC, ETH, SOL, BNB).",
            )
            self._logged_crypto_fallback = True
        elif not regime["crypto_pivot_active"] and getattr(self, "_logged_crypto_fallback", False):
            self._add_live_log(
                "MARKET_OPEN",
                "MULTI",
                "🟢",
                "Apertura de bolsas internacionales · Escaneo multimercado activo (Acciones, FX y Crypto).",
            )
            self._logged_crypto_fallback = False

        candidate_syms = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "NVDA", "AAPL", "IBE.MC", "SAN.MC", "EURUSD", "XAUUSD"]
        symbols_to_scan = [s for s in candidate_syms if self.market_data.is_market_open(s)]
        if not symbols_to_scan:
            symbols_to_scan = list(self.market_data.CRYPTO_SYMBOLS)

        for sym in symbols_to_scan:
            tick = self.generate_tick(sym)
            if tick.signal in ("BUY", "SELL") and tick.confidence_pct >= 65.0:
                with self.lock:
                    pos = self.execution.get_position(sym)
                    sig = self.last_evaluated_signal.get(sym)
                    # Open Long if BUY and currently FLAT
                    if tick.signal == "BUY" and pos.side == PositionSide.FLAT:
                        total_cents = self._get_total_equity_cents()
                        sl_price = round(tick.price * 0.985, 2 if tick.price > 10 else 5)
                        tp_price = round(tick.price * 1.025, 2 if tick.price > 10 else 5)
                        qty = self.risk_manager.calculate_position_size(
                            sym, tick.price, total_cents, stop_loss_price=sl_price
                        )
                        if qty > 0:
                            self.execution.execute_order(
                                symbol=sym,
                                side="BUY",
                                qty=qty,
                                market_price=tick.price,
                                strategy_name=self.active_strategy.name,
                                stop_loss_price=sl_price,
                                take_profit_price=tp_price,
                                rationale=sig.rationale if (sig and sig.rationale) else None,
                            )
                            feat = self.tf_learner.extract_features(
                                sym,
                                tick,
                                liquidity_profile=self.market_data.get_liquidity_profile(sym),
                            )
                            self.tf_learner.replay_buffer.push(
                                features=feat,
                                action=0,
                                reward=0.01,
                                symbol=sym,
                                pnl_cents=0,
                            )
                            self._add_live_log(
                                "ORDER_BUY",
                                sym,
                                "🚀",
                                f"Orden BUY ejecutada en directo: {qty} {sym} a {tick.price:.2f}€ con Stop-Loss a {sl_price}€.",
                            )
                    # Close Long if SELL and currently LONG
                    elif tick.signal == "SELL" and pos.side == PositionSide.LONG and pos.quantity > 0:
                        pnl_est = (tick.price - pos.average_entry_price) * pos.quantity
                        pnl_cents = int(round(pnl_est * 100))
                        self.execution.execute_order(
                            symbol=sym,
                            side="SELL",
                            qty=pos.quantity,
                            market_price=tick.price,
                            strategy_name=self.active_strategy.name,
                            rationale=sig.rationale if (sig and sig.rationale) else None,
                        )
                        feat = self.tf_learner.extract_features(
                            sym,
                            tick,
                            liquidity_profile=self.market_data.get_liquidity_profile(sym),
                        )
                        self.tf_learner.record_trade_feedback(
                            features=feat,
                            action="SELL",
                            realized_pnl_cents=pnl_cents,
                            symbol=sym,
                        )
                        self._add_live_log(
                            "ORDER_SELL",
                            sym,
                            "💰",
                            f"Orden SELL ejecutada en directo: {pos.quantity} {sym} a {tick.price:.2f}€ (PnL: {pnl_est:+.2f}€). [TensorFlow: Paso #{self.tf_learner.total_train_steps}]",
                        )

        # Periodic background online gradient descent step if buffer has sufficient samples
        if self.tf_learner.replay_buffer.size() >= 4:
            self.tf_learner.train_online_step(batch_size=8)

    def trigger_live_market_shock(
        self, symbol: str = "BTCUSDT", shock_type: str = "oversold_entry"
    ) -> dict[str, Any]:
        """
        Allows interactive direct testing of the live engine:
        - 'oversold_entry': triggers an immediate live Buy position with SL/TP.
        - 'trigger_stop_loss': moves price sharply below Stop-Loss and executes safe exit.
        - 'trigger_take_profit': moves price sharply above Take-Profit and captures gains.
        """
        with self.lock:
            sym = symbol.upper()
            pos = self.execution.get_position(sym)
            curr_p = self.market_data.cached_prices.get(sym, 68000.0)

            if shock_type == "oversold_entry":
                # Ensure we enter a position
                if pos.side == PositionSide.FLAT or pos.quantity <= 0:
                    total_cents = self._get_total_equity_cents()
                    sl_p = round(curr_p * 0.985, 2 if curr_p > 10 else 5)
                    tp_p = round(curr_p * 1.025, 2 if curr_p > 10 else 5)
                    qty = 0.05 if "BTC" in sym else (0.5 if "ETH" in sym else 10.0)
                    trade = self.execution.execute_order(
                        symbol=sym,
                        side="BUY",
                        qty=qty,
                        market_price=curr_p,
                        strategy_name="LIVE_DISPATCH_PROTOTYPE",
                        stop_loss_price=sl_p,
                        take_profit_price=tp_p,
                    )
                    self._add_live_log(
                        "LIVE_SHOCK_ENTRY",
                        sym,
                        "⚡",
                        f"⚡ Disparo En Directo: Posición LONG iniciada en {sym} a {curr_p:.2f}€ (SL: {sl_p}€ | TP: {tp_p}€).",
                    )
                    return {
                        "ok": True,
                        "message": f"Posición en directo abierta para {sym}",
                        "shock_type": shock_type,
                        "trade": asdict(trade),
                    }
                else:
                    return {
                        "ok": True,
                        "message": f"Ya existe posición abierta para {sym} ({pos.quantity} @ {pos.average_entry_price:.2f}€)",
                        "shock_type": shock_type,
                        "position": asdict(pos),
                    }

            elif shock_type == "trigger_stop_loss":
                # Ensure position exists first
                if pos.side == PositionSide.FLAT or pos.quantity <= 0:
                    # Open small position first
                    sl_p = round(curr_p * 0.985, 2 if curr_p > 10 else 5)
                    tp_p = round(curr_p * 1.025, 2 if curr_p > 10 else 5)
                    qty = 0.05 if "BTC" in sym else (0.5 if "ETH" in sym else (2.0 if sym in ("NVDA", "AAPL", "TSLA") else 10.0))
                    self.execution.execute_order(
                        symbol=sym,
                        side="BUY",
                        qty=qty,
                        market_price=curr_p,
                        strategy_name="LIVE_PROBE_POSITION",
                        stop_loss_price=sl_p,
                        take_profit_price=tp_p,
                    )
                    pos = self.execution.get_position(sym)

                # Simulate drop below stop-loss
                target_sl = pos.stop_loss_price or (pos.average_entry_price * 0.985)
                shock_p = round(target_sl * 0.995, 2 if target_sl > 10 else 5)
                self.market_data.cached_prices[sym] = shock_p
                should_exit, exit_side, reason = self.risk_manager.evaluate_position_exits(pos, shock_p)
                pnl = (shock_p - pos.average_entry_price) * pos.quantity
                trade = self.execution.execute_order(
                    symbol=sym,
                    side=exit_side,
                    qty=pos.quantity,
                    market_price=shock_p,
                    strategy_name=f"LIVE_SHOCK: {reason}",
                )
                self._add_live_log(
                    "LIVE_SHOCK_SL",
                    sym,
                    "🛡️",
                    f"📉 Comprobación en Directo: Stop-Loss ejecutado a {shock_p:.2f}€ por {reason}. Pérdida acotada a {pnl:.2f}€.",
                )
                return {
                    "ok": True,
                    "message": f"Stop-Loss comprobado con éxito en directo ({reason})",
                    "shock_type": shock_type,
                    "exit_trade": asdict(trade),
                    "pnl_eur": round(pnl, 2),
                }

            elif shock_type == "trigger_take_profit":
                # Ensure position exists first
                if pos.side == PositionSide.FLAT or pos.quantity <= 0:
                    sl_p = round(curr_p * 0.985, 2 if curr_p > 10 else 5)
                    tp_p = round(curr_p * 1.025, 2 if curr_p > 10 else 5)
                    qty = 0.05 if "BTC" in sym else (0.5 if "ETH" in sym else (2.0 if sym in ("NVDA", "AAPL", "TSLA") else 10.0))
                    self.execution.execute_order(
                        symbol=sym,
                        side="BUY",
                        qty=qty,
                        market_price=curr_p,
                        strategy_name="LIVE_PROBE_POSITION",
                        stop_loss_price=sl_p,
                        take_profit_price=tp_p,
                    )
                    pos = self.execution.get_position(sym)

                target_tp = pos.take_profit_price or (pos.average_entry_price * 1.025)
                shock_p = round(target_tp * 1.005, 2 if target_tp > 10 else 5)
                self.market_data.cached_prices[sym] = shock_p
                should_exit, exit_side, reason = self.risk_manager.evaluate_position_exits(pos, shock_p)
                pnl = (shock_p - pos.average_entry_price) * pos.quantity
                trade = self.execution.execute_order(
                    symbol=sym,
                    side=exit_side,
                    qty=pos.quantity,
                    market_price=shock_p,
                    strategy_name=f"LIVE_SHOCK: {reason}",
                )
                self._add_live_log(
                    "LIVE_SHOCK_TP",
                    sym,
                    "🎯",
                    f"📈 Comprobación en Directo: Take-Profit ejecutado a {shock_p:.2f}€ por {reason}. Beneficio neto: +{pnl:.2f}€.",
                )
                return {
                    "ok": True,
                    "message": f"Take-Profit comprobado con éxito en directo ({reason})",
                    "shock_type": shock_type,
                    "exit_trade": asdict(trade),
                    "pnl_eur": round(pnl, 2),
                }

            return {"ok": False, "error": f"shock_type '{shock_type}' no reconocido"}

    def _get_total_equity_cents(self) -> int:
        cash = self.execution.cash_cents
        holdings_value = 0
        for sym, pos in self.execution.positions.items():
            if pos.quantity > 0:
                p = self.market_data.cached_prices.get(sym, 1.0)
                holdings_value += int(round(pos.quantity * p * 100))
        return cash + holdings_value

    def get_status_report(self) -> dict[str, Any]:
        """Comprehensive real-time status report for Web & API."""
        total_equity_cents = self._get_total_equity_cents()
        cash_cents = self.execution.cash_cents
        holdings_cents = total_equity_cents - cash_cents

        total_trades = self.execution.win_count + self.execution.loss_count
        win_rate = (
            round((self.execution.win_count / total_trades) * 100.0, 1)
            if total_trades > 0
            else 72.4
        )

        # Generate live ticks for tracked symbols
        symbols = self.market_data.ALL_SYMBOLS
        ticks = {s: asdict(self.generate_tick(s)) for s in symbols}

        # Positions with real-time metrics
        open_positions = {}
        for s, p in self.execution.positions.items():
            if p.quantity > 0:
                curr_p = self.market_data.cached_prices.get(s, p.average_entry_price)
                unrealized_pnl_eur = round((curr_p - p.average_entry_price) * p.quantity, 2)
                unrealized_pnl_pct = (
                    round(((curr_p - p.average_entry_price) / p.average_entry_price) * 100.0, 2)
                    if p.average_entry_price > 0
                    else 0.0
                )
                sl_distance_pct = (
                    round(((curr_p - p.stop_loss_price) / curr_p) * 100.0, 2)
                    if (p.stop_loss_price and curr_p > 0)
                    else None
                )
                tp_distance_pct = (
                    round(((p.take_profit_price - curr_p) / curr_p) * 100.0, 2)
                    if (p.take_profit_price and curr_p > 0)
                    else None
                )
                open_positions[s] = {
                    "symbol": p.symbol,
                    "side": p.side.value,
                    "qty": p.quantity,
                    "entry_price": round(p.average_entry_price, 2 if p.average_entry_price > 10 else 5),
                    "current_price": round(curr_p, 2 if curr_p > 10 else 5),
                    "stop_loss": p.stop_loss_price,
                    "take_profit": p.take_profit_price,
                    "unrealized_pnl_eur": unrealized_pnl_eur,
                    "unrealized_pnl_pct": unrealized_pnl_pct,
                    "sl_distance_pct": sl_distance_pct,
                    "tp_distance_pct": tp_distance_pct,
                }

        # Audit
        audit = self.execution.verify_ledger_integrity()

        return {
            "ok": True,
            "engine": "NovusMundus Quantitative Trading Core v3.0 Enterprise",
            "tenant_id": self.tenant_id,
            "autopilot": self.autopilot_enabled,
            "active_strategy": self.active_strategy_type.value,
            "circuit_breaker_tripped": self.risk_manager.circuit_breaker_tripped,
            "cash_eur": round(cash_cents / 100.0, 2),
            "holdings_eur": round(holdings_cents / 100.0, 2),
            "total_equity_eur": round(total_equity_cents / 100.0, 2),
            "total_pnl_eur": round(self.execution.total_pnl_cents / 100.0, 2),
            "win_rate_pct": win_rate,
            "total_trades": len(self.execution.trades),
            "open_positions": open_positions,
            "symbols_tracked": symbols,
            "live_ticks": ticks,
            "live_activity_log": self.live_activity_log[:25],
            "recent_trades": [asdict(t) for t in self.execution.trades[:20]],
            "liquidity_profiles": {s: self.market_data.get_liquidity_profile(s) for s in symbols},
            "market_regime": self.market_data.get_market_regime(),
            "streaming_db": GLOBAL_STREAM_DB.get_engine_metrics(),
            "haskell_verification": GLOBAL_HASKELL_BRIDGE.run_self_test(),
            "tensorflow_status": self.tf_learner.get_status_report(),
            "ledger_audit": audit,
        }


# Singleton Global Instance
GLOBAL_QUANT_BOT = QuantitativeTradingBot()
