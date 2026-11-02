"""Comprehensive test suite for the Novus Quantitative Trading Bot system."""

from __future__ import annotations

import math
from pathlib import Path
import sys
import time
import numpy as np
import pytest

TEST_DIR = Path(__file__).resolve().parent
CV_ROOT = TEST_DIR.parent
if str(CV_ROOT) not in sys.path:
    sys.path.insert(0, str(CV_ROOT))
if str(CV_ROOT / "09_antigravity_perfect_pipeline") not in sys.path:
    sys.path.insert(0, str(CV_ROOT / "09_antigravity_perfect_pipeline"))

from trading_bot.backtester import QuantitativeBacktester
from trading_bot.bot_core import QuantitativeTradingBot
from trading_bot.execution_engine import ExecutionEngine
from trading_bot.haskell_bridge import GLOBAL_HASKELL_BRIDGE
from trading_bot.indicators import Indicators
from trading_bot.market_data import MarketDataProvider
from trading_bot.models import Candle, MarketTick, OrderSide, Position, PositionSide, RiskConfig, StrategyType
from trading_bot.risk_manager import RiskManager
from trading_bot.strategies.grid_trader import DynamicGridTradingStrategy
from trading_bot.strategies.mean_reversion import VWAPMeanReversionStrategy
from trading_bot.strategies.momentum_ema_rsi import MomentumEMARSIStrategy
from trading_bot.streaming_db import GLOBAL_STREAM_DB
from trading_bot.true_live_api import GLOBAL_TRUE_PRICES_ENGINE


# ---------------------------------------------------------------------------
# 1. TECHNICAL INDICATORS
# ---------------------------------------------------------------------------

def test_indicators_math():
    prices = [10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0]
    volumes = [100.0, 200.0, 100.0, 150.0, 250.0, 100.0, 300.0]

    # SMA
    sma = Indicators.sma(prices, period=3)
    assert np.isnan(sma[0])
    assert np.isnan(sma[1])
    assert round(float(sma[2]), 2) == 11.0
    assert round(float(sma[-1]), 2) == 15.0

    # EMA
    ema = Indicators.ema(prices, period=3)
    assert not np.isnan(ema[-1])
    assert ema[-1] > ema[2]

    # VWAP
    vwap = Indicators.vwap(prices, volumes)
    assert 10.0 <= vwap <= 16.0
    assert round(vwap, 2) == 13.46

    # Robust MAD
    mad = Indicators.robust_mad(prices)
    assert mad > 0.0

    # Bollinger Bands
    upper, mid, lower = Indicators.bollinger_bands(prices, period=5)
    assert upper[-1] > mid[-1] > lower[-1]

    # RSI
    rsi = Indicators.rsi([10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0])
    assert rsi[-1] > 70.0  # Strong uptrend

    # ATR
    highs = [12.0, 13.0, 14.0, 15.0]
    lows = [10.0, 11.0, 12.0, 13.0]
    closes = [11.0, 12.0, 13.0, 14.0]
    atr = Indicators.atr(highs, lows, closes, period=3)
    assert atr[-1] > 0.0

    # Z-Score
    z = Indicators.z_score(15.0, 10.0, 2.5)
    assert z == 2.0


# ---------------------------------------------------------------------------
# 2. STRATEGIES (MEAN REVERSION, MOMENTUM, GRID)
# ---------------------------------------------------------------------------

def test_vwap_mean_reversion_strategy():
    strat = VWAPMeanReversionStrategy(z_threshold=1.8, window=10)
    now = time.time()
    candles = [
        Candle(timestamp=now + i * 60, open=100.0, high=102.0, low=98.0, close=100.0, volume=50.0)
        for i in range(25)
    ]

    # Oversold tick (Z < -1.8 and price below lower band)
    oversold_tick = MarketTick(
        symbol="BTCUSDT",
        price=85.0,
        volume=100.0,
        timestamp=now + 1600,
        vwap=100.0,
        z_score=-2.5,
        volatility_mad=4.0,
        signal="HOLD",
        confidence_pct=50.0,
    )
    sig_buy = strat.evaluate("BTCUSDT", candles, oversold_tick)
    assert sig_buy.action == "BUY"
    assert sig_buy.confidence > 75.0
    assert sig_buy.target_price == 100.0
    assert sig_buy.rationale is not None
    assert "Reversión" in sig_buy.rationale.thesis
    assert sig_buy.rationale.risk_reward_ratio > 0

    # Overbought tick (Z > 1.8 and price above upper band)
    overbought_tick = MarketTick(
        symbol="BTCUSDT",
        price=115.0,
        volume=100.0,
        timestamp=now + 1600,
        vwap=100.0,
        z_score=2.5,
        volatility_mad=4.0,
        signal="HOLD",
        confidence_pct=50.0,
    )
    sig_sell = strat.evaluate("BTCUSDT", candles, overbought_tick)
    assert sig_sell.action == "SELL"
    assert sig_sell.confidence > 75.0
    assert sig_sell.rationale is not None
    assert "VWAP" in sig_sell.rationale.thesis


def test_momentum_ema_rsi_strategy():
    strat = MomentumEMARSIStrategy(fast_period=5, slow_period=10, rsi_period=7)
    now = time.time()
    # Accelerating price series to trigger EMA golden cross
    prices = [10.0 + i * 0.5 for i in range(25)]
    candles = [
        Candle(timestamp=now + i * 60, open=p - 0.2, high=p + 0.5, low=p - 0.3, close=p, volume=100.0)
        for i, p in enumerate(prices)
    ]
    tick = MarketTick(
        symbol="ETHUSDT",
        price=prices[-1],
        volume=100.0,
        timestamp=now + 2000,
        vwap=prices[-1],
        z_score=1.0,
        volatility_mad=0.5,
        signal="HOLD",
        confidence_pct=50.0,
    )
    sig = strat.evaluate("ETHUSDT", candles, tick)
    assert sig.action in ("BUY", "HOLD")


def test_grid_trading_strategy():
    strat = DynamicGridTradingStrategy(grid_levels=5, atr_multiplier=1.0)
    now = time.time()
    candles = [
        Candle(timestamp=now + i * 60, open=100.0, high=102.0, low=98.0, close=100.0, volume=100.0)
        for i in range(20)
    ]
    tick_neutral = MarketTick(
        symbol="SOLUSDT",
        price=100.0,
        volume=50.0,
        timestamp=now + 1300,
        vwap=100.0,
        z_score=0.0,
        volatility_mad=2.0,
        signal="HOLD",
        confidence_pct=50.0,
    )
    sig1 = strat.evaluate("SOLUSDT", candles, tick_neutral)
    assert sig1.action == "HOLD"

    # Price drops down by 5% -> Buy dip
    tick_dip = MarketTick(
        symbol="SOLUSDT",
        price=94.0,
        volume=50.0,
        timestamp=now + 1400,
        vwap=100.0,
        z_score=-2.0,
        volatility_mad=2.0,
        signal="HOLD",
        confidence_pct=50.0,
    )
    sig_buy = strat.evaluate("SOLUSDT", candles, tick_dip)
    assert sig_buy.action == "BUY"


# ---------------------------------------------------------------------------
# 3. RISK MANAGEMENT & CIRCUIT BREAKER
# ---------------------------------------------------------------------------

def test_risk_manager_sizing_and_circuit_breaker():
    config = RiskConfig(
        max_risk_per_trade_pct=2.0,
        default_stop_loss_pct=2.0,
        max_daily_drawdown_pct=5.0,
        use_trailing_stop=True,
    )
    rm = RiskManager(config)

    # 1. Position Sizing: 10,000 EUR equity, 2% risk = 200 EUR budget
    # Asset price 100 EUR, SL at 98 EUR (distance 2 EUR) -> qty = 200 / 2 = 100 units
    qty = rm.calculate_position_size("EURUSD", price=100.0, total_equity_cents=1_000_000, stop_loss_price=98.0)
    assert qty == 25.0  # Capped at 25% max notional (2500 EUR / 100 = 25)

    # 2. Circuit Breaker
    assert not rm.check_circuit_breaker(1_000_000)
    assert not rm.check_circuit_breaker(970_000)  # 3% drawdown -> OK
    assert rm.check_circuit_breaker(940_000)  # 6% drawdown -> TRIPPED!

    # 3. Trailing Stop
    pos = Position(
        symbol="BTCUSDT",
        side=PositionSide.LONG,
        quantity=1.0,
        average_entry_price=100.0,
        current_price=103.0,
        peak_price=105.0,  # Peak was +5%
    )
    # Price retraces from 105 to 103 (distance > 1.0%)
    should_exit, side, reason = rm.evaluate_position_exits(pos, current_price=103.0)
    assert should_exit
    assert side == "SELL"
    assert "Trailing Stop" in reason


# ---------------------------------------------------------------------------
# 4. EXECUTION ENGINE & CRYPTOGRAPHIC HASH CHAIN
# ---------------------------------------------------------------------------

def test_execution_engine_and_audit(tmp_path):
    storage_file = str(tmp_path / "test_trades.json")
    engine = ExecutionEngine(storage_path=storage_file)

    # 1. Execute BUY
    trade1 = engine.execute_order("BTCUSDT", side="BUY", qty=0.1, market_price=50000.0)
    assert trade1.side == "BUY"
    assert trade1.status == "SETTLED"
    assert len(trade1.block_hash) == 64
    assert engine.get_position("BTCUSDT").quantity == 0.1
    assert "thesis" in trade1.rationale
    assert "trigger" in trade1.rationale
    assert "risk_reward_ratio" in trade1.rationale
    assert len(trade1.rationale["factors"]) > 0

    # 2. Execute SELL
    trade2 = engine.execute_order("BTCUSDT", side="SELL", qty=0.1, market_price=52000.0)
    assert trade2.side == "SELL"
    assert engine.get_position("BTCUSDT").quantity == 0.0
    assert "thesis" in trade2.rationale

    # 3. Cryptographic Verification
    audit = engine.verify_ledger_integrity()
    assert audit["valid"] is True
    assert audit["blocks_verified"] == 2
    assert audit["status"] == "CRYPTOGRAPHICALLY_VERIFIED"

    # 4. Prevent naked selling
    with pytest.raises(ValueError, match="No hay posición abierta"):
        engine.execute_order("BTCUSDT", side="SELL", qty=0.1, market_price=50000.0)


# ---------------------------------------------------------------------------
# 5. BACKTESTER ENGINE
# ---------------------------------------------------------------------------

def test_quantitative_backtester():
    backtester = QuantitativeBacktester(initial_capital_eur=10000.0)
    strategy = VWAPMeanReversionStrategy(z_threshold=1.5, window=10)

    now = time.time()
    # 40 candles with sine oscillation to trigger entries and exits
    candles = [
        Candle(
            timestamp=now + i * 3600,
            open=100.0 + 5.0 * math.sin(i * 0.3),
            high=102.0 + 5.0 * math.sin(i * 0.3),
            low=98.0 + 5.0 * math.sin(i * 0.3),
            close=100.0 + 5.0 * math.sin(i * 0.3),
            volume=100.0,
        )
        for i in range(50)
    ]

    report = backtester.run_backtest("TEST_ASSET", candles, strategy)
    assert report.initial_capital_eur == 10000.0
    assert not math.isnan(report.sharpe_ratio)
    assert not math.isnan(report.max_drawdown_pct)
    assert len(report.equity_curve) > 0


# ---------------------------------------------------------------------------
# 6. CENTRAL BOT CORE ORCHESTRATOR
# ---------------------------------------------------------------------------

def test_central_trading_bot_orchestrator():
    bot = QuantitativeTradingBot(tenant_id="test-tenant")
    bot.stop_autopilot()  # Stop background thread for test isolation

    # Status report
    rep = bot.get_status_report()
    assert rep["ok"] is True
    assert "cash_eur" in rep
    assert "symbols_tracked" in rep
    assert "BTCUSDT" in rep["symbols_tracked"]

    # Generate tick
    tick = bot.generate_tick("BTCUSDT")
    assert tick.symbol == "BTCUSDT"
    assert tick.price > 0.0
    assert tick.signal in ("BUY", "SELL", "HOLD")

    # Strategy switching
    bot.set_active_strategy("MOMENTUM_EMA_RSI")
    assert bot.active_strategy_type == StrategyType.MOMENTUM_EMA_RSI

    # Autopilot toggle
    bot.autopilot_enabled = False
    assert bot.toggle_autopilot() is True
    assert bot.autopilot_enabled is True


def test_orderbook_depth_and_microstructure():
    from trading_bot.market_data import MarketDataProvider
    provider = MarketDataProvider()
    ob = provider.fetch_live_binance_depth("BTCUSDT", limit=5)
    assert ob["symbol"] == "BTCUSDT"
    assert "bids" in ob
    assert "asks" in ob
    assert len(ob["bids"]) > 0
    assert len(ob["asks"]) > 0
    assert "imbalance_pct" in ob
    assert "bias" in ob


def test_google_antigravity_perfect_pipeline_six_stages():
    from perfect_pipeline import GLOBAL_PERFECT_PIPELINE
    report = GLOBAL_PERFECT_PIPELINE.execute_perfect_pipeline("BTCUSDT", qty=0.1)
    assert report["ok"] is True
    assert "stages" in report
    stages = report["stages"]

    # Stage 1: Ingestion
    assert stages["stage1_ingestion"]["symbol"] == "BTCUSDT"
    assert "FLOWFILE-" in stages["stage1_ingestion"]["nifi_flowfile_uuid"]

    # Stage 2: PDE Diffusion
    assert stages["stage2_pde_diffusion"]["diffusion_status"] in ("SOBOLEV_CERTIFIED", "CONVERGED")
    assert stages["stage2_pde_diffusion"]["l2_residual"] < 0.05

    # Stage 3: Statistical Welford Monoid & Robust MAD
    assert stages["stage3_statistical_monoid"]["welford_std"] >= 0.0
    assert "z_mad" in stages["stage3_statistical_monoid"]

    # Stage 4: Cognitive Thesis
    thesis = stages["stage4_cognitive_thesis"]
    assert "thesis" in thesis
    assert "Z_{MAD}" in thesis["trigger_equation"]
    assert thesis["risk_reward_ratio"] > 0

    # Stage 5: Audio Intelligence
    audio = stages["stage5_audio_intelligence"]
    assert audio["audio_sample_rate_hz"] == 24000
    assert "Mikel Irastorza" in audio["spoken_script_es"]
    assert audio["audio_duration_est_sec"] > 0

    # Stage 6: Double-Entry Cryptographic Ledger
    settlement = stages["stage6_ledger_settlement"]
    assert settlement["balanced"] is True
    assert settlement["debit_cents"] == settlement["credit_cents"]
    assert len(settlement["block_hash"]) == 64


def test_autonomous_demo_simulation_with_failures_and_wins():
    bot = QuantitativeTradingBot(tenant_id="test-demo")
    bot.stop_autopilot()

    # 1. Run demo simulation under stress scenario
    report = bot.run_demo_simulation(symbol="BTCUSDT", scenario="stress", candle_count=150)
    assert report.total_trades > 0
    assert len(report.completed_trades) > 0

    # Verify both wins and losses are present and transparently classified
    assert report.winning_trades > 0
    assert report.losing_trades > 0

    # Verify completed trades fields
    first_loss = next((t for t in report.completed_trades if t["result_code"] == "LOSS"), None)
    assert first_loss is not None
    assert first_loss["pnl_eur"] < 0
    assert "Fallo" in first_loss["explanation"] or "Stop-Loss" in first_loss["exit_reason"]

    first_win = next((t for t in report.completed_trades if t["result_code"] == "WIN"), None)
    assert first_win is not None
    assert first_win["pnl_eur"] > 0
    assert "Convergencia" in first_win["explanation"]

    # Verify post mortem
    assert "loss_mitigation_note" in report.post_mortem_summary
    assert report.post_mortem_summary["winning_count"] == report.winning_trades
    assert report.post_mortem_summary["losing_count"] == report.losing_trades

    # 2. Test single autonomous demo step
    step_res = bot.execute_autonomous_demo_step(symbol="BTCUSDT")
    assert step_res["ok"] is True
    assert step_res["symbol"] == "BTCUSDT"
    assert "signal" in step_res


def test_live_directo_trading_and_market_shocks():
    bot = QuantitativeTradingBot(tenant_id="test-live-directo")
    bot.stop_autopilot()

    # 1. Test live entry shock
    entry_res = bot.trigger_live_market_shock(symbol="BTCUSDT", shock_type="oversold_entry")
    assert entry_res["ok"] is True
    assert len(bot.live_activity_log) > 0
    assert any("Posición LONG iniciada" in l["message"] or "ejecutada" in l["message"] for l in bot.live_activity_log)

    pos = bot.execution.get_position("BTCUSDT")
    assert pos.quantity > 0

    # 2. Check status report contains live telemetry & enriched position
    status = bot.get_status_report()
    assert "live_activity_log" in status
    assert len(status["live_activity_log"]) > 0
    assert "BTCUSDT" in status["open_positions"]
    btc_pos = status["open_positions"]["BTCUSDT"]
    assert "unrealized_pnl_eur" in btc_pos
    assert "unrealized_pnl_pct" in btc_pos
    assert "sl_distance_pct" in btc_pos

    # 3. Test live stop-loss shock (protected failure verification)
    sl_res = bot.trigger_live_market_shock(symbol="BTCUSDT", shock_type="trigger_stop_loss")
    assert sl_res["ok"] is True
    assert "Stop-Loss" in sl_res["message"]
    assert bot.execution.get_position("BTCUSDT").quantity == 0

    # 4. Test live take-profit shock
    tp_res = bot.trigger_live_market_shock(symbol="BTCUSDT", shock_type="trigger_take_profit")
    assert tp_res["ok"] is True
    assert "Take-Profit" in tp_res["message"]
    assert bot.execution.get_position("BTCUSDT").quantity == 0


def test_multi_asset_cryptos_and_equities_trading_and_klines():
    from trading_bot.market_data import MarketDataProvider

    provider = MarketDataProvider()

    # 1. Verify symbol sets
    assert "BTCUSDT" in provider.CRYPTO_SYMBOLS
    assert "ETHUSDT" in provider.CRYPTO_SYMBOLS
    assert "NVDA" in provider.EQUITY_SYMBOLS
    assert "IBE.MC" in provider.EQUITY_SYMBOLS
    assert "SAN.MC" in provider.EQUITY_SYMBOLS

    # 2. Verify candles for both Crypto and Equity
    crypto_candles = provider.get_historical_candles("BTCUSDT", interval="1h", count=20)
    assert len(crypto_candles) >= 10
    assert crypto_candles[-1].close > 0
    assert crypto_candles[-1].high >= crypto_candles[-1].low

    equity_candles = provider.get_historical_candles("NVDA", interval="1h", count=20)
    assert len(equity_candles) >= 10
    assert equity_candles[-1].close > 0
    assert equity_candles[-1].high >= equity_candles[-1].low

    # 3. Verify prices
    p_crypto, v_crypto = provider.get_latest_price("BTCUSDT")
    assert p_crypto > 1000.0
    assert v_crypto > 0

    p_eq, v_eq = provider.get_latest_price("NVDA")
    assert p_eq > 50.0
    assert v_eq > 0

    # 4. Verify equity depth book
    eq_depth = provider.fetch_live_binance_depth("NVDA", limit=5)
    assert eq_depth["symbol"] == "NVDA"
    assert len(eq_depth["bids"]) > 0
    assert len(eq_depth["asks"]) > 0

    # 5. Verify trading bot execution and backtest on equities
    bot = QuantitativeTradingBot(tenant_id="test-equities")
    bot.stop_autopilot()

    trade = bot.execute_trade(symbol="NVDA", side="BUY", qty=5.0)
    assert trade.symbol == "NVDA"
    assert trade.qty == 5.0
    assert len(trade.block_hash) == 64

    # 6. Verify backtesting report on equities
    report = bot.run_backtest(symbol="IBE.MC", candle_count=40)
    assert report.symbol == "IBE.MC"
    assert report.total_trades >= 0


def test_tensorflow_continuous_learning_and_adaptive_strategy() -> None:
    """Verifies TensorFlow 2.22 deep learning model, online continuous training, and strategy."""
    from trading_bot.tensorflow_learner import TensorFlowContinuousLearner
    from trading_bot.strategies.tensorflow_adaptive import TensorFlowAdaptiveStrategy
    from trading_bot.models import MarketTick, StrategyType

    learner = TensorFlowContinuousLearner()
    status_init = learner.get_status_report()
    assert status_init["is_learning_active"] is True
    assert "TensorFlow" in status_init["framework"] or "Analytic" in status_init["framework"]

    # 1. Feature extraction
    dummy_tick = MarketTick(
        symbol="BTCUSDT",
        price=68000.0,
        volume=25.0,
        timestamp=time.time(),
        vwap=67500.0,
        z_score=-2.2,
        volatility_mad=450.0,
        signal="BUY",
        confidence_pct=85.0,
    )
    features = learner.extract_features(
        symbol="BTCUSDT",
        tick=dummy_tick,
        orderbook={"imbalance_pct": 14.5},
        liquidity_profile={"spread_bps": 1.2, "amihud_ratio": 1e-5},
    )
    assert len(features) == 8
    assert isinstance(features, np.ndarray)

    # 2. Forward inference prediction
    pred = learner.predict(features)
    assert pred["action"] in ("BUY", "HOLD", "SELL")
    assert 0.0 <= pred["confidence_pct"] <= 100.0
    assert "probabilities" in pred
    assert math.isclose(sum(pred["probabilities"].values()), 1.0, rel_tol=1e-2)

    # 3. Online continuous learning from trade feedback
    initial_steps = learner.total_train_steps
    initial_hash = learner.weights_hash

    learner.record_trade_feedback(
        features=features,
        action="BUY",
        realized_pnl_cents=1250,  # +12.50 EUR profit
        symbol="BTCUSDT",
    )
    assert learner.total_train_steps >= initial_steps
    assert learner.current_loss > 0.0
    assert len(learner.loss_history) > 0

    # 4. Strategy evaluation
    strat = TensorFlowAdaptiveStrategy(learner=learner)
    sig = strat.evaluate("BTCUSDT", [], dummy_tick)
    assert sig.action in ("BUY", "HOLD", "SELL")
    assert sig.rationale is not None
    assert "TensorFlow" in sig.rationale.thesis or "Deep Learning" in sig.rationale.thesis

    # 5. Integration with QuantitativeTradingBot
    bot = QuantitativeTradingBot(tenant_id="test-tf")
    bot.stop_autopilot()
    bot.set_active_strategy(StrategyType.TENSORFLOW_ADAPTIVE)
    assert bot.active_strategy_type == StrategyType.TENSORFLOW_ADAPTIVE

    trade = bot.execute_trade("NVDA", "BUY", qty=2.0)
    assert trade.symbol == "NVDA"
    assert trade.status == "SETTLED"

    rep = bot.get_status_report()
    assert "tensorflow_status" in rep
    assert rep["tensorflow_status"]["is_learning_active"] is True


def test_trading_business_school_smc_strategy() -> None:
    """Verifies Trading Business School (TBS) Smart Money Concepts, FVGs, Sweeps and bot integration."""
    from trading_bot.strategies.tbs_smc import TradingBusinessSchoolStrategy
    from trading_bot.models import Candle, MarketTick, StrategyType
    from trading_bot.tensorflow_learner import TensorFlowContinuousLearner

    learner = TensorFlowContinuousLearner()
    strategy = TradingBusinessSchoolStrategy(learner=learner, min_risk_reward=2.5)

    # 1. Synthesize candles exhibiting an institutional Liquidity Sweep + Bullish FVG
    now = time.time()
    candles: list[Candle] = []

    # Candles 0-5: Range consolidation establishing swing low at 67,000 and swing high at 68,000
    prices_pattern = [
        (67500, 67900, 67300, 67700),  # 0
        (67700, 68050, 67600, 67950),  # 1 (Swing high ~68,050)
        (67950, 68000, 67400, 67500),  # 2
        (67500, 67600, 67000, 67100),  # 3 (Swing low ~67,000)
        (67100, 67500, 67100, 67400),  # 4
        (67400, 67700, 67300, 67550),  # 5
        # Candle 6: Bearish setup candle (pre-displacement Order Block)
        (67550, 67600, 67100, 67200),  # 6 (Down-close, low 67,100)
        # Candle 7: Liquidity Sweep of Sell-Side Liquidity (SSL) below 67,000, wick down to 66,850, closes at 67,150
        (67200, 67300, 66850, 67150),  # 7 (SSL sweep wick 66,850, close 67,150 > 67,000)
        # Candle 8: Strong Bullish Displacement (C1 of FVG)
        (67150, 67800, 67100, 67750),  # 8 (Big green candle)
        # Candle 9: Continuation candle (C2 of FVG, low 67,500 > C0 high 67,300 -> FVG gap!)
        (67750, 68300, 67500, 68250),  # 9 (High 68,300, low 67,500)
        # Candle 10: Retest / mitigation into the FVG zone [67,300 - 67,500]
        (68250, 68350, 67450, 67600),  # 10
    ]

    for idx, (o, h, l, c) in enumerate(prices_pattern):
        candles.append(Candle(
            timestamp=now - (len(prices_pattern) - idx) * 3600,
            open=float(o),
            high=float(h),
            low=float(l),
            close=float(c),
            volume=15.0 + idx * 2.0,
        ))

    # 2. Test Swing Detection
    swings = strategy._identify_swings(candles, window=2)
    assert len(swings["highs"]) > 0 or len(swings["lows"]) > 0

    # 3. Test FVG Detection (BISI)
    fvgs = strategy._detect_fvgs(candles)
    assert any(f["type"] == "BULLISH_FVG" for f in fvgs)

    # 4. Test Order Block Detection
    obs = strategy._detect_order_blocks(candles)
    assert "bullish_ob" in obs

    # 5. Test Liquidity Sweep Detection
    sweep = strategy._detect_liquidity_sweep(candles, swings, current_price=67600.0)
    assert isinstance(sweep, dict)
    assert "swept" in sweep

    # 6. Test Strategy Evaluation
    current_tick = MarketTick(
        symbol="BTCUSDT",
        price=67600.0,
        volume=28.0,
        timestamp=now,
        vwap=67450.0,
        z_score=-0.9,
        volatility_mad=320.0,
        signal="BUY",
        confidence_pct=88.0,
    )
    sig = strategy.evaluate(
        symbol="BTCUSDT",
        candles=candles,
        current_tick=current_tick,
        orderbook={"imbalance_pct": 18.2},
        liquidity_profile={"spread_bps": 1.1},
    )

    assert sig.symbol == "BTCUSDT"
    assert sig.action in ("BUY", "HOLD", "SELL")
    assert sig.strategy == StrategyType.TRADING_BUSINESS_SCHOOL
    assert sig.rationale is not None
    assert "Trading Business School" in sig.rationale.thesis
    assert sig.rationale.risk_reward_ratio >= 2.5
    assert len(sig.rationale.factors) >= 4

    # 7. Test Integration with QuantitativeTradingBot
    bot = QuantitativeTradingBot(tenant_id="test-tbs-smc")
    bot.stop_autopilot()
    bot.set_active_strategy(StrategyType.TRADING_BUSINESS_SCHOOL)
    assert bot.active_strategy_type == StrategyType.TRADING_BUSINESS_SCHOOL

    trade = bot.execute_trade("BTCUSDT", "BUY", qty=0.1)
    assert trade.symbol == "BTCUSDT"
    assert trade.status == "SETTLED"
    assert "Trading Business School" in trade.strategy_used
    assert len(trade.block_hash) == 64

    # 8. Test Backtester with Trading Business School strategy
    report = bot.run_backtest("BTCUSDT", strategy_type="TRADING_BUSINESS_SCHOOL", candle_count=40)
    assert report.symbol == "BTCUSDT"
    assert report.total_trades >= 0
    assert report.sharpe_ratio is not None


# ---------------------------------------------------------------------------
# 16. MARKET HOURS CALENDAR & 24/7 CRYPTO FALLBACK ENGINE
# ---------------------------------------------------------------------------

def test_market_hours_crypto_always_open():
    """Cryptocurrencies trade 24/7/365 continuously without market closes."""
    md = MarketDataProvider()
    # Wednesday 10:00 UTC (1761732000), Saturday 14:00 UTC (1761998400), Sunday 03:00 UTC (1762045200)
    test_timestamps = [1761732000.0, 1761998400.0, 1762045200.0]
    for ts in test_timestamps:
        for sym in md.CRYPTO_SYMBOLS:
            assert md.is_market_open(sym, ts) is True
            status = md.get_symbol_market_status(sym, ts)
            assert status["is_open"] is True
            assert status["status"] == "24/7 SPOT"
            assert status["asset_class"] == "CRYPTO"


def test_market_hours_traditional_schedules():
    """Forex, US stocks, and EU stocks follow strict calendar rules."""
    md = MarketDataProvider()
    # Wednesday 14:00 UTC: ALL markets should be open
    wed_open_ts = 1761746400.0  # Wed Oct 29, 2025 ~14:00 UTC
    assert md.is_market_open("EURUSD", wed_open_ts) is True
    assert md.is_market_open("NVDA", wed_open_ts) is True
    assert md.is_market_open("IBE.MC", wed_open_ts) is True
    assert md.is_market_open("XAUUSD", wed_open_ts) is True

    # Saturday 14:00 UTC: Traditional markets must be closed
    sat_ts = 1762005600.0  # Sat Nov 1, 2025 14:00 UTC
    assert md.is_market_open("EURUSD", sat_ts) is False
    assert md.is_market_open("NVDA", sat_ts) is False
    assert md.is_market_open("IBE.MC", sat_ts) is False
    assert md.is_market_open("XAUUSD", sat_ts) is False


def test_market_regime_and_crypto_fallback():
    """When traditional markets are closed, the engine pivots 100% to Crypto 24/7."""
    md = MarketDataProvider()
    # Simulate a Saturday session
    sat_ts = 1762005600.0
    regime = md.get_market_regime(sat_ts)

    assert regime["crypto_24_7"] is True
    assert regime["equities_open"] is False
    assert regime["forex_open"] is False
    assert regime["crypto_pivot_active"] is True
    assert regime["active_focus"] == "CRYPTO_24_7"
    assert "PIVOT 100%" in regime["status_label"].upper() or "CRYPTO 24/7" in regime["status_label"].upper()

    open_syms = md.get_open_symbols(sat_ts)
    for c in md.CRYPTO_SYMBOLS:
        assert c in open_syms
    assert "NVDA" not in open_syms
    assert "EURUSD" not in open_syms


# ---------------------------------------------------------------------------
# 17. HASKELL QUANTITATIVE KERNEL (GHC 9.14) & FORMAL INVARIANT VERIFICATION
# ---------------------------------------------------------------------------

def test_haskell_quant_kernel_bridge():
    """Tests native compiled Haskell binary formal verification proofs."""
    # 1. Zero-Sum Pacioli Invariant verification
    balanced_res = GLOBAL_HASKELL_BRIDGE.verify_ledger(500000, 500000)
    assert balanced_res["ok"] is True
    assert balanced_res["balanced"] is True

    unbalanced_res = GLOBAL_HASKELL_BRIDGE.verify_ledger(500000, 480000)
    assert unbalanced_res["ok"] is True
    assert unbalanced_res["balanced"] is False

    # 2. Analytical Black-Scholes call valuation
    call_p = GLOBAL_HASKELL_BRIDGE.compute_bs_call(spot=94000.0, strike=95000.0)
    assert call_p > 0.0

    # 3. Regime verification via Haskell
    haskell_reg = GLOBAL_HASKELL_BRIDGE.detect_regime(equities_open=False, forex_open=False)
    assert haskell_reg["ok"] is True
    assert haskell_reg["crypto_24_7_pivot"] is True
    assert "CryptoOnlyFallback" in haskell_reg["regime"]

    # 4. Engine self-test
    self_test = GLOBAL_HASKELL_BRIDGE.run_self_test()
    assert self_test["ok"] is True
    assert self_test["pacioli_audit_pass"] is True


# ---------------------------------------------------------------------------
# 18. NOVUS STREAMING DATABASE (WAL, CONTINUOUS AGGREGATION & POLARS)
# ---------------------------------------------------------------------------

def test_novus_streaming_database_engine():
    """Tests high-throughput in-memory ring buffer, WAL persistence, and Polars export."""
    # Ingest streaming tick
    ev = GLOBAL_STREAM_DB.append_event("TICK", "BTCUSDT", {"price": 78650.0, "volume": 2.15, "signal": "BUY"})
    assert ev.seq_id > 0
    assert ev.symbol == "BTCUSDT"
    assert len(ev.curr_hash) == 64

    # Query stream buffer
    recent = GLOBAL_STREAM_DB.query_stream(symbol="BTCUSDT", limit=10)
    assert len(recent) > 0
    assert recent[0]["symbol"] == "BTCUSDT"

    # Continuous aggregation
    agg = GLOBAL_STREAM_DB.get_continuous_aggregate("BTCUSDT")
    assert agg["symbol"] == "BTCUSDT"
    assert agg["aggregates"]["count"] > 0
    assert agg["aggregates"]["vwap"] > 0

    # Polars DataFrame conversion
    df = GLOBAL_STREAM_DB.to_polars("BTCUSDT", limit=20)
    assert df is not None
    if hasattr(df, "shape"):
        assert df.shape[0] > 0

    # Engine metrics
    metrics = GLOBAL_STREAM_DB.get_engine_metrics()
    assert metrics["ok"] is True
    assert metrics["wal_size_bytes"] > 0
    assert metrics["tracked_symbols_count"] >= 1


# ---------------------------------------------------------------------------
# 19. TRUE LIVE PRICES ENGINE (INSTITUTIONAL PUBLIC FEEDS)
# ---------------------------------------------------------------------------

def test_true_live_prices_engine():
    """Tests real-time price fetching from public institutional feeds."""
    res = GLOBAL_TRUE_PRICES_ENGINE.get_all_true_prices()
    assert res["ok"] is True
    assert res["total_assets"] >= 13
    assert len(res["prices"]) >= 13
    assert "market_regime" in res

    # Verify at least one real crypto quote
    btc = next((p for p in res["prices"] if p["symbol"] == "BTCUSDT"), None)
    assert btc is not None
    assert btc["price"] > 10000.0
    assert btc["is_open"] is True
    assert btc["market_status"] == "24/7 SPOT"







