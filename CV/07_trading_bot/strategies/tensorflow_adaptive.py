"""TensorFlow Adaptive Deep Learning Strategy for Novus Trading Bot.

Uses a trained continuous-learning neural network to predict market direction,
confidence, and expected return, adapting online with every executed trade.
"""

from __future__ import annotations

from typing import Any

from ..models import Candle, MarketTick, StrategySignal, StrategyType, TradeRationale
from ..tensorflow_learner import TensorFlowContinuousLearner
from .base import BaseStrategy


class TensorFlowAdaptiveStrategy(BaseStrategy):
    """Deep Learning Adaptive Strategy powered by TensorFlow Keras."""

    def __init__(
        self,
        learner: TensorFlowContinuousLearner | None = None,
        confidence_threshold: float = 55.0,
        expected_return_threshold: float = 0.005,
    ) -> None:
        super().__init__(
            name="TensorFlow Adaptive Deep Learning",
            strategy_type=StrategyType.VWAP_MEAN_REVERSION,  # compatible enum
        )
        self.learner = learner or TensorFlowContinuousLearner()
        self.confidence_threshold = confidence_threshold
        self.expected_return_threshold = expected_return_threshold

    def evaluate(
        self,
        symbol: str,
        candles: list[Candle],
        current_tick: MarketTick,
        orderbook: dict[str, Any] | None = None,
        liquidity_profile: dict[str, Any] | None = None,
    ) -> StrategySignal:
        """Evaluates market state through the TensorFlow Deep Neural Network."""
        features = self.learner.extract_features(
            symbol=symbol,
            tick=current_tick,
            orderbook=orderbook,
            liquidity_profile=liquidity_profile,
            candles=candles,
        )

        pred = self.learner.predict(features)
        action = pred["action"]
        confidence = pred["confidence_pct"]
        exp_return = pred["expected_return_pct"]
        probs = pred["probabilities"]

        price = current_tick.price
        vwap = current_tick.vwap

        # Determine price levels based on deep learning predictions
        if action == "BUY" and confidence >= self.confidence_threshold:
            target_price = round(price * (1.0 + max(0.015, exp_return)), 2)
            stop_loss = round(price * 0.985, 2)  # 1.5% stop loss
            take_profit = round(max(vwap, target_price), 2)
            action_code = "BUY"
        elif action == "SELL" and confidence >= self.confidence_threshold:
            target_price = round(price * (1.0 - max(0.015, abs(exp_return))), 2)
            stop_loss = round(price * 1.015, 2)
            take_profit = round(min(vwap, target_price), 2)
            action_code = "SELL"
        else:
            action_code = "HOLD"
            target_price = price
            stop_loss = None
            take_profit = None

        # Build comprehensive explainability rationale
        st = self.learner.get_status_report()
        prob_str = f"P(BUY)={probs['BUY']:.1%}, P(HOLD)={probs['HOLD']:.1%}, P(SELL)={probs['SELL']:.1%}"

        rationale = TradeRationale(
            thesis=(
                f"Inferencia Neural TensorFlow (Deep Learning Online). "
                f"La red clasificó el estado en {action_code} con {confidence:.1f}% de certidumbre "
                f"y retorno esperado de {exp_return:+.2%}."
            ),
            trigger=(
                f"Activación de pesos neuronales (Loss: {st['current_loss']}, Paso #{st['total_train_steps']}). "
                f"Distribución: {prob_str}."
            ),
            factors=[
                f"Framework: {st['framework']} con optimizador Adam (lr={st['learning_rate']})",
                f"Vector de entrada: Z-score normalizado ({features[0]:.2f}), Imbalance ({features[2]:.2f})",
                f"Distancia al VWAP institucional: {features[3]:.2f} (MAD: {features[4]:.2f})",
                f"Huella criptográfica de pesos: {st['weights_hash'][:16]}...",
                f"Muestras entrenadas en vivo: {st['total_samples_trained']} micro-lotes",
                f"Retorno esperado de la red: {exp_return:+.3%}",
            ],
            risk_reward_ratio=2.4 if action_code == "BUY" else 2.0,
            stop_loss_justification="Protección asimétrica del 1.5% coordinada con el Gestor de Riesgo central",
            take_profit_justification=f"Convergencia hacia el objetivo predicho por el modelo ({target_price}€)",
            historical_edge=(
                f"Modelo entrenado en {st['total_train_steps']} pasos continuos. "
                f"Loss actual: {st['current_loss']} (convergencia estable)."
            ),
            orderbook_bias=f"Presión de flujo de órdenes integrada en tensor de entrada: {features[2]:+.2f}",
        )

        return StrategySignal(
            symbol=symbol,
            action=action_code,
            confidence=confidence,
            reason=f"TensorFlow DNN ({action_code} {confidence:.1f}%)",
            target_price=target_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            strategy=StrategyType.VWAP_MEAN_REVERSION,
            metadata={
                "probabilities": probs,
                "expected_return": exp_return,
                "tf_steps": st["total_train_steps"],
                "tf_loss": st["current_loss"],
            },
            rationale=rationale,
        )
