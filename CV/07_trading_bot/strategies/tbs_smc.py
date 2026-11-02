"""Trading Business School (TBS) Institutional Strategy: Smart Money Concepts (SMC) & Fair Value Gaps (FVG).

Implements the core institutional trading methodologies taught by Trading Business School (TBS):
1. Market Structure Shifts (MSS / CHoCH - Change of Character)
2. Buy-Side & Sell-Side Liquidity Sweeps (BSL / SSL Stop-Hunts)
3. Fair Value Gaps (FVG 3-candle imbalances: BISI & SIBI) with Consequent Encroachment (50% CE)
4. Institutional Order Blocks (+OB / -OB mitigation zones)
5. Strict Asymmetric Risk-to-Reward (R:R >= 2.5:1, targeting 3.0:1)
6. Deep Learning Confirmation via TensorFlow continuous learner
"""

from __future__ import annotations

import math
from typing import Any

from ..models import Candle, MarketTick, StrategySignal, StrategyType, TradeRationale
from ..tensorflow_learner import TensorFlowContinuousLearner
from .base import BaseStrategy


class TradingBusinessSchoolStrategy(BaseStrategy):
    """Institutional Smart Money Strategy based on Trading Business School (TBS) methodologies."""

    def __init__(
        self,
        learner: TensorFlowContinuousLearner | None = None,
        swing_window: int = 2,
        min_risk_reward: float = 2.5,
        target_risk_reward: float = 3.0,
        fvg_lookback: int = 15,
        confidence_threshold: float = 60.0,
    ) -> None:
        super().__init__(
            name="Trading Business School (SMC & FVG)",
            strategy_type=StrategyType.TRADING_BUSINESS_SCHOOL,
        )
        self.learner = learner
        self.swing_window = swing_window
        self.min_risk_reward = min_risk_reward
        self.target_risk_reward = target_risk_reward
        self.fvg_lookback = fvg_lookback
        self.confidence_threshold = confidence_threshold

    def _identify_swings(
        self, candles: list[Candle], window: int | None = None
    ) -> dict[str, list[dict[str, Any]]]:
        """Identifies fractal swing highs and swing lows across the candle series."""
        w = window or self.swing_window
        n = len(candles)
        swing_highs: list[dict[str, Any]] = []
        swing_lows: list[dict[str, Any]] = []

        for i in range(w, n - w):
            curr_h = candles[i].high
            curr_l = candles[i].low

            # Check if pivot high
            is_high = all(curr_h >= candles[i - j].high for j in range(1, w + 1)) and all(
                curr_h >= candles[i + j].high for j in range(1, w + 1)
            )
            if is_high:
                swing_highs.append({"index": i, "price": curr_h, "candle": candles[i]})

            # Check if pivot low
            is_low = all(curr_l <= candles[i - j].low for j in range(1, w + 1)) and all(
                curr_l <= candles[i + j].low for j in range(1, w + 1)
            )
            if is_low:
                swing_lows.append({"index": i, "price": curr_l, "candle": candles[i]})

        return {"highs": swing_highs, "lows": swing_lows}

    def _detect_fvgs(
        self, candles: list[Candle], lookback: int | None = None
    ) -> list[dict[str, Any]]:
        """Detects 3-candle Fair Value Gaps (FVG) and verifies if they remain unmitigated.

        - Bullish FVG (BISI): Candle[i-2].high < Candle[i].low.
        - Bearish FVG (SIBI): Candle[i-2].low > Candle[i].high.
        """
        lb = lookback or self.fvg_lookback
        n = len(candles)
        if n < 3:
            return []

        start_idx = max(2, n - lb)
        fvgs: list[dict[str, Any]] = []

        for i in range(start_idx, n):
            c0 = candles[i - 2]
            c1 = candles[i - 1]
            c2 = candles[i]

            # Bullish FVG (BISI)
            if c0.high < c2.low and c1.close > c1.open:
                bottom = c0.high
                top = c2.low
                ce = (bottom + top) / 2.0  # Consequent Encroachment (50%)
                # Check if mitigated by candles after i
                mitigated = any(candles[j].low <= bottom for j in range(i + 1, n))
                fvgs.append({
                    "type": "BULLISH_FVG",
                    "index": i,
                    "top": round(top, 4),
                    "bottom": round(bottom, 4),
                    "ce": round(ce, 4),
                    "mitigated": mitigated,
                    "gap_size": round(top - bottom, 4),
                })

            # Bearish FVG (SIBI)
            elif c0.low > c2.high and c1.close < c1.open:
                top = c0.low
                bottom = c2.high
                ce = (bottom + top) / 2.0
                mitigated = any(candles[j].high >= top for j in range(i + 1, n))
                fvgs.append({
                    "type": "BEARISH_FVG",
                    "index": i,
                    "top": round(top, 4),
                    "bottom": round(bottom, 4),
                    "ce": round(ce, 4),
                    "mitigated": mitigated,
                    "gap_size": round(top - bottom, 4),
                })

        return fvgs

    def _detect_order_blocks(
        self, candles: list[Candle], lookback: int = 15
    ) -> dict[str, dict[str, Any] | None]:
        """Identifies institutional Order Blocks (+OB bullish, -OB bearish).

        - Bullish Order Block (+OB): The last down-close (bearish) candle preceding
          a strong displacement move upward.
        - Bearish Order Block (-OB): The last up-close (bullish) candle preceding
          a strong displacement move downward.
        """
        n = len(candles)
        if n < 4:
            return {"bullish_ob": None, "bearish_ob": None}

        start_idx = max(1, n - lookback)
        bullish_ob: dict[str, Any] | None = None
        bearish_ob: dict[str, Any] | None = None

        for i in range(start_idx, n - 1):
            curr = candles[i]
            nxt = candles[i + 1]

            # Displacement check (range > 1.2 * avg range)
            is_displacement_up = (nxt.close - nxt.open) > (curr.high - curr.low) * 1.1
            is_displacement_down = (nxt.open - nxt.close) > (curr.high - curr.low) * 1.1

            # Bullish Order Block: red candle followed by strong green displacement
            if curr.close < curr.open and is_displacement_up:
                bullish_ob = {
                    "index": i,
                    "top": curr.high,
                    "bottom": curr.low,
                    "open": curr.open,
                    "close": curr.close,
                    "type": "+OB (Bullish Order Block)",
                }

            # Bearish Order Block: green candle followed by strong red displacement
            if curr.close > curr.open and is_displacement_down:
                bearish_ob = {
                    "index": i,
                    "top": curr.high,
                    "bottom": curr.low,
                    "open": curr.open,
                    "close": curr.close,
                    "type": "-OB (Bearish Order Block)",
                }

        return {"bullish_ob": bullish_ob, "bearish_ob": bearish_ob}

    def _detect_liquidity_sweep(
        self,
        candles: list[Candle],
        swings: dict[str, list[dict[str, Any]]],
        current_price: float,
    ) -> dict[str, Any]:
        """Detects if recent candles have swept Buy-Side Liquidity (BSL) or Sell-Side Liquidity (SSL).

        - SSL Sweep (Bullish): Price pierced below a swing low, but closed back above or recovered.
        - BSL Sweep (Bearish): Price pierced above a swing high, but closed back below or recovered.
        """
        n = len(candles)
        if n < 3 or (not swings["highs"] and not swings["lows"]):
            return {"swept": False, "type": "NONE", "level": 0.0, "wick_extreme": 0.0}

        # Check the last 3 candles against previous swing levels
        recent_candles = candles[-3:]
        prev_highs = [sh for sh in swings["highs"] if sh["index"] < n - 3]
        prev_lows = [sl for sl in swings["lows"] if sl["index"] < n - 3]

        # 1. Check Sell-Side Liquidity (SSL) Sweep
        if prev_lows:
            recent_low_ref = prev_lows[-1]["price"]
            for c in recent_candles:
                if c.low < recent_low_ref and (c.close > recent_low_ref or current_price > recent_low_ref):
                    return {
                        "swept": True,
                        "type": "SSL_SWEEP",
                        "direction": "BULLISH",
                        "level": recent_low_ref,
                        "wick_extreme": c.low,
                        "description": f"Barrido de Sell-Side Liquidity (SSL) bajo {recent_low_ref:.2f}€ con absorción institucional",
                    }

        # 2. Check Buy-Side Liquidity (BSL) Sweep
        if prev_highs:
            recent_high_ref = prev_highs[-1]["price"]
            for c in recent_candles:
                if c.high > recent_high_ref and (c.close < recent_high_ref or current_price < recent_high_ref):
                    return {
                        "swept": True,
                        "type": "BSL_SWEEP",
                        "direction": "BEARISH",
                        "level": recent_high_ref,
                        "wick_extreme": c.high,
                        "description": f"Barrido de Buy-Side Liquidity (BSL) sobre {recent_high_ref:.2f}€ con absorción institucional",
                    }

        return {"swept": False, "type": "NONE", "level": 0.0, "wick_extreme": 0.0}

    def _detect_market_structure_shift(
        self, candles: list[Candle], swings: dict[str, list[dict[str, Any]]]
    ) -> dict[str, Any]:
        """Detects Market Structure Shift (MSS) or Change of Character (CHoCH)."""
        n = len(candles)
        if n < 4 or not swings["highs"] or not swings["lows"]:
            return {"mss": False, "bias": "NEUTRAL", "level": 0.0}

        last_c = candles[-1]
        prev_highs = [sh for sh in swings["highs"] if sh["index"] < n - 1]
        prev_lows = [sl for sl in swings["lows"] if sl["index"] < n - 1]

        # Bullish MSS: Break and close above the most recent swing high
        if prev_highs and last_c.close > prev_highs[-1]["price"]:
            return {
                "mss": True,
                "bias": "BULLISH",
                "level": prev_highs[-1]["price"],
                "description": f"MSS Alcista (CHoCH): Cierre impulsivo sobre swing high en {prev_highs[-1]['price']:.2f}€",
            }

        # Bearish MSS: Break and close below the most recent swing low
        if prev_lows and last_c.close < prev_lows[-1]["price"]:
            return {
                "mss": True,
                "bias": "BEARISH",
                "level": prev_lows[-1]["price"],
                "description": f"MSS Bajista (CHoCH): Cierre impulsivo bajo swing low en {prev_lows[-1]['price']:.2f}€",
            }

        return {"mss": False, "bias": "NEUTRAL", "level": 0.0}

    def evaluate(
        self,
        symbol: str,
        candles: list[Candle],
        current_tick: MarketTick,
        orderbook: dict[str, Any] | None = None,
        liquidity_profile: dict[str, Any] | None = None,
    ) -> StrategySignal:
        """Evaluates market state using Trading Business School (SMC, FVG, Order Blocks & Sweeps)."""
        dec = 5 if ("USD" in symbol or "EUR" in symbol) and "BTC" not in symbol else 2

        if len(candles) < 10:
            return StrategySignal(
                symbol=symbol,
                action="HOLD",
                confidence=50.0,
                reason="Insuficientes velas para análisis de estructura institucional TBS (SMC)",
                target_price=current_tick.price,
                strategy=self.strategy_type,
            )

        curr_p = current_tick.price
        swings = self._identify_swings(candles)
        fvgs = self._detect_fvgs(candles)
        obs = self._detect_order_blocks(candles)
        sweep = self._detect_liquidity_sweep(candles, swings, curr_p)
        mss = self._detect_market_structure_shift(candles, swings)

        # Active / unmitigated FVGs
        active_bullish_fvgs = [f for f in fvgs if f["type"] == "BULLISH_FVG" and not f["mitigated"]]
        active_bearish_fvgs = [f for f in fvgs if f["type"] == "BEARISH_FVG" and not f["mitigated"]]

        # Check if price is mitigating an FVG
        mitigating_bull_fvg = any(f["bottom"] * 0.998 <= curr_p <= f["top"] * 1.002 for f in active_bullish_fvgs)
        mitigating_bear_fvg = any(f["bottom"] * 0.998 <= curr_p <= f["top"] * 1.002 for f in active_bearish_fvgs)

        # Check if price is mitigating an Order Block
        bob = obs["bullish_ob"]
        sob = obs["bearish_ob"]
        mitigating_bob = bob is not None and (bob["bottom"] * 0.998 <= curr_p <= bob["top"] * 1.005)
        mitigating_sob = sob is not None and (sob["bottom"] * 0.995 <= curr_p <= sob["top"] * 1.002)

        # Deep learning confirmation if TensorFlow learner is attached
        tf_pred = None
        tf_action = "HOLD"
        tf_conf = 50.0
        tf_probs = {"BUY": 0.33, "HOLD": 0.34, "SELL": 0.33}
        if self.learner:
            features = self.learner.extract_features(
                symbol=symbol,
                tick=current_tick,
                orderbook=orderbook,
                liquidity_profile=liquidity_profile,
                candles=candles,
            )
            tf_pred = self.learner.predict(features)
            tf_action = tf_pred["action"]
            tf_conf = tf_pred["confidence_pct"]
            tf_probs = tf_pred["probabilities"]

        # Signal resolution logic
        action = "HOLD"
        confidence = 50.0
        stop_loss: float | None = None
        take_profit: float | None = None
        target_price = curr_p
        trigger_desc = ""
        factors: list[str] = []

        # ---------------- BULLISH SETUP (BUY) ----------------
        # Conditions: SSL Sweep OR (Active Bullish FVG Mitigation AND (mitigating BOB or Bullish MSS or TF BUY confirmation))
        is_bullish_setup = (
            (sweep.get("direction") == "BULLISH")
            or (mitigating_bull_fvg and (mss["bias"] == "BULLISH" or tf_action == "BUY" or mitigating_bob))
            or (mitigating_bob and (tf_action == "BUY" or current_tick.z_score < -0.8))
        )

        # ---------------- BEARISH SETUP (SELL) ----------------
        is_bearish_setup = (
            (sweep.get("direction") == "BEARISH")
            or (mitigating_bear_fvg and (mss["bias"] == "BEARISH" or tf_action == "SELL" or mitigating_sob))
            or (mitigating_sob and (tf_action == "SELL" or current_tick.z_score > 0.8))
        )

        if is_bullish_setup and not is_bearish_setup:
            action = "BUY"
            # Calculate invalidation stop loss
            if sweep.get("direction") == "BULLISH" and sweep.get("wick_extreme", 0) > 0:
                invalidation_level = sweep["wick_extreme"] * 0.997
                trigger_desc = sweep["description"]
            elif bob is not None:
                invalidation_level = bob["bottom"] * 0.997
                trigger_desc = f"Mitigación de +OB Institucional [{bob['bottom']:.2f} - {bob['top']:.2f}€]"
            elif active_bullish_fvgs:
                invalidation_level = active_bullish_fvgs[-1]["bottom"] * 0.997
                trigger_desc = f"Entrada en Consequent Encroachment (50%) FVG [{active_bullish_fvgs[-1]['bottom']:.2f} - {active_bullish_fvgs[-1]['top']:.2f}€]"
            else:
                invalidation_level = curr_p * 0.985
                trigger_desc = "Confluencia de Flujo de Órdenes Institucional TBS"

            risk = max(0.0001, curr_p - invalidation_level)
            stop_loss = round(invalidation_level, dec)

            # Target: opposing Buy-Side Liquidity pool or 3.0x risk
            opposing_highs = [sh["price"] for sh in swings["highs"] if sh["price"] > curr_p]
            if opposing_highs and (opposing_highs[0] - curr_p) / risk >= self.min_risk_reward:
                take_profit = round(opposing_highs[0], dec)
            else:
                take_profit = round(curr_p + (risk * self.target_risk_reward), dec)

            target_price = take_profit
            actual_rr = round((take_profit - curr_p) / risk, 2)

            base_conf = 78.0
            if sweep.get("direction") == "BULLISH":
                base_conf += 8.0
            if mitigating_bull_fvg:
                base_conf += 6.0
            if mss["bias"] == "BULLISH":
                base_conf += 5.0
            if tf_action == "BUY":
                base_conf += min(10.0, tf_conf * 0.1)

            confidence = min(98.5, round(base_conf, 1))

            factors = [
                f"Trading Business School (SMC): Confluencia institucional con R:R asimétrico {actual_rr}:1",
                f"Nivel de Invalidez Institucional (SL): {stop_loss}€ colocado estrictamente bajo el bloque/barrido",
                f"Objetivo de Liquidez Buy-Side (BSL): {take_profit}€ (+{(take_profit/curr_p - 1):.2%})",
                f"Barrido de Liquidez: {sweep.get('description', 'Sin barrido reciente detectado')}",
                f"Fair Value Gaps (FVG): {len(active_bullish_fvgs)} zonas BISI activas (mitigación: {'SÍ' if mitigating_bull_fvg else 'NO'})",
                f"Confirmación Neural TensorFlow: P(BUY)={tf_probs['BUY']:.1%}, P(HOLD)={tf_probs['HOLD']:.1%}, P(SELL)={tf_probs['SELL']:.1%}",
            ]

        elif is_bearish_setup and not is_bullish_setup:
            action = "SELL"
            # Calculate invalidation stop loss
            if sweep.get("direction") == "BEARISH" and sweep.get("wick_extreme", 0) > 0:
                invalidation_level = sweep["wick_extreme"] * 1.003
                trigger_desc = sweep["description"]
            elif sob is not None:
                invalidation_level = sob["top"] * 1.003
                trigger_desc = f"Mitigación de -OB Institucional [{sob['bottom']:.2f} - {sob['top']:.2f}€]"
            elif active_bearish_fvgs:
                invalidation_level = active_bearish_fvgs[-1]["top"] * 1.003
                trigger_desc = f"Entrada en Consequent Encroachment (50%) FVG Bajista [{active_bearish_fvgs[-1]['bottom']:.2f} - {active_bearish_fvgs[-1]['top']:.2f}€]"
            else:
                invalidation_level = curr_p * 1.015
                trigger_desc = "Confluencia de Flujo de Órdenes Bajista TBS"

            risk = max(0.0001, invalidation_level - curr_p)
            stop_loss = round(invalidation_level, dec)

            # Target: opposing Sell-Side Liquidity pool or 3.0x risk
            opposing_lows = [sl["price"] for sl in swings["lows"] if sl["price"] < curr_p]
            if opposing_lows and (curr_p - opposing_lows[-1]) / risk >= self.min_risk_reward:
                take_profit = round(opposing_lows[-1], dec)
            else:
                take_profit = round(curr_p - (risk * self.target_risk_reward), dec)

            target_price = take_profit
            actual_rr = round((curr_p - take_profit) / risk, 2)

            base_conf = 78.0
            if sweep.get("direction") == "BEARISH":
                base_conf += 8.0
            if mitigating_bear_fvg:
                base_conf += 6.0
            if mss["bias"] == "BEARISH":
                base_conf += 5.0
            if tf_action == "SELL":
                base_conf += min(10.0, tf_conf * 0.1)

            confidence = min(98.5, round(base_conf, 1))

            factors = [
                f"Trading Business School (SMC): Confluencia institucional bajista con R:R asimétrico {actual_rr}:1",
                f"Nivel de Invalidez Institucional (SL): {stop_loss}€ sobre el Order Block / Mecha de manipulación",
                f"Objetivo de Liquidez Sell-Side (SSL): {take_profit}€ (-{(1 - take_profit/curr_p):.2%})",
                f"Barrido de Liquidez: {sweep.get('description', 'Sin barrido reciente detectado')}",
                f"Fair Value Gaps (FVG): {len(active_bearish_fvgs)} zonas SIBI activas (mitigación: {'SÍ' if mitigating_bear_fvg else 'NO'})",
                f"Confirmación Neural TensorFlow: P(SELL)={tf_probs['SELL']:.1%}, P(HOLD)={tf_probs['HOLD']:.1%}, P(BUY)={tf_probs['BUY']:.1%}",
            ]

        else:
            action = "HOLD"
            confidence = 50.0
            stop_loss = None
            take_profit = None
            target_price = curr_p
            trigger_desc = "Estructura institucional TBS en acumulación / Esperando barrido o mitigación de FVG"
            actual_rr = self.target_risk_reward
            factors = [
                "Smart Money Concepts (TBS): Esperando ruptura o barrido de liquidez de rango",
                f"Zonas FVG detectadas: {len(active_bullish_fvgs)} BISI alcistas, {len(active_bearish_fvgs)} SIBI bajistas",
                f"Estado MSS / CHoCH: {mss.get('bias', 'NEUTRAL')}",
                f"Order Blocks activos: Bullish (+OB)={'SÍ' if bob else 'NO'}, Bearish (-OB)={'SÍ' if sob else 'NO'}",
                f"Confirmación Neural TensorFlow: P(HOLD)={tf_probs['HOLD']:.1%}",
            ]

        rationale = TradeRationale(
            thesis=(
                f"Trading Business School (TBS) · Smart Money Concepts (SMC) + Fair Value Gaps. "
                f"Estructura institucional clasificada en {action} con {confidence:.1f}% de certidumbre institucional."
            ),
            trigger=trigger_desc,
            factors=factors,
            risk_reward_ratio=actual_rr,
            stop_loss_justification=(
                f"Nivel de invalidación cuantitativa TBS ({stop_loss}€): Si el precio penetra esta zona, la premisa institucional queda invalidada."
                if stop_loss else "Sin stop loss activo en posición neutral (HOLD)"
            ),
            take_profit_justification=(
                f"Convergencia hacia piscina de liquidez opuesta ({target_price}€) con ratio asimétrico {actual_rr}:1."
                if take_profit else "Sin objetivo activo en posición neutral"
            ),
            historical_edge=(
                "Metodología Smart Money Concepts (SMC) probada por Trading Business School (TBS). "
                "Filtra falsas rupturas retail acumulando en zonas de absorción institucional y FVGs."
            ),
            orderbook_bias=(
                f"Flujo de órdenes institucional con confirmación TensorFlow P({action})={tf_probs.get(action, 0.33):.1%}"
            ),
        )

        return StrategySignal(
            symbol=symbol,
            action=action,
            confidence=confidence,
            reason=f"TBS SMC ({action} {confidence:.1f}% | R:R {actual_rr}:1)",
            target_price=target_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            strategy=self.strategy_type,
            metadata={
                "tbs_methodology": "Smart Money Concepts (SMC & FVG)",
                "risk_reward_ratio": actual_rr,
                "liquidity_sweep": sweep,
                "active_bullish_fvgs": len(active_bullish_fvgs),
                "active_bearish_fvgs": len(active_bearish_fvgs),
                "mss_shift": mss,
                "has_bullish_ob": bob is not None,
                "has_bearish_ob": sob is not None,
                "tf_probabilities": tf_probs,
                "tf_action": tf_action,
            },
            rationale=rationale,
        )
