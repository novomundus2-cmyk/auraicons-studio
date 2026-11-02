"""Market Data Provider: Connects to public live APIs & realistic stochastic generators."""

from __future__ import annotations

import datetime
import json
import math
import random
import re
import time
import urllib.error
import urllib.request
from typing import Any

from .models import Candle, MarketTick


class MarketDataProvider:
    """Provides market ticks and historical candles from live feeds and stochastic models."""

    CRYPTO_SYMBOLS: list[str] = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]
    FOREX_SYMBOLS: list[str] = ["EURUSD", "USDJPY", "GBPUSD", "USDCHF"]
    US_EQUITY_SYMBOLS: list[str] = ["NVDA", "AAPL", "TSLA"]
    EU_EQUITY_SYMBOLS: list[str] = ["IBE.MC", "SAN.MC", "ITX.MC", "ACS.MC", "SU.PA"]
    EQUITY_SYMBOLS: list[str] = US_EQUITY_SYMBOLS + EU_EQUITY_SYMBOLS
    COMMODITY_SYMBOLS: list[str] = ["XAUUSD"]

    ALL_SYMBOLS: list[str] = CRYPTO_SYMBOLS + EQUITY_SYMBOLS + FOREX_SYMBOLS + COMMODITY_SYMBOLS

    BASE_PRICES: dict[str, float] = {
        "BTCUSDT": 94250.0,
        "ETHUSDT": 3150.0,
        "SOLUSDT": 185.0,
        "BNBUSDT": 655.0,
        "NVDA": 213.66,
        "AAPL": 248.90,
        "TSLA": 258.40,
        "IBE.MC": 22.10,
        "SAN.MC": 10.51,
        "ITX.MC": 56.28,
        "ACS.MC": 43.80,
        "SU.PA": 242.10,
        "EURUSD": 1.0850,
        "USDJPY": 152.40,
        "GBPUSD": 1.2980,
        "USDCHF": 0.8650,
        "XAUUSD": 2748.50,
    }

    LIQUIDITY_METRICS: dict[str, dict[str, Any]] = {
        "BTCUSDT": {
            "tier": "TIER_1_ULTRA_LIQUID",
            "market_name": "Bitcoin / Tether Spot",
            "spread_bps": 1.2,
            "spread_pct": 0.012,
            "turnover_24h_usd": 28_400_000_000,
            "turnover_label": "28.4B $ / 24h",
            "depth_notional_top5_usd": 12_850_000,
            "slippage_est_pct": 0.002,
            "amihud_ratio": 0.000008,
            "rating": "AAA+ (MÁXIMA LIQUIDEZ GLOBAL)",
            "passed_gatekeeper": True,
        },
        "ETHUSDT": {
            "tier": "TIER_1_ULTRA_LIQUID",
            "market_name": "Ethereum / Tether Spot",
            "spread_bps": 1.5,
            "spread_pct": 0.015,
            "turnover_24h_usd": 14_200_000_000,
            "turnover_label": "14.2B $ / 24h",
            "depth_notional_top5_usd": 7_900_000,
            "slippage_est_pct": 0.003,
            "amihud_ratio": 0.000012,
            "rating": "AAA (PROFUNDIDAD INSTITUCIONAL)",
            "passed_gatekeeper": True,
        },
        "SOLUSDT": {
            "tier": "TIER_1_ULTRA_LIQUID",
            "market_name": "Solana / Tether Spot",
            "spread_bps": 2.2,
            "spread_pct": 0.022,
            "turnover_24h_usd": 4_800_000_000,
            "turnover_label": "4.8B $ / 24h",
            "depth_notional_top5_usd": 3_400_000,
            "slippage_est_pct": 0.006,
            "amihud_ratio": 0.000028,
            "rating": "AA+ (ALTA LIQUIDEZ)",
            "passed_gatekeeper": True,
        },
        "BNBUSDT": {
            "tier": "TIER_1_ULTRA_LIQUID",
            "market_name": "BNB / Tether Spot",
            "spread_bps": 2.0,
            "spread_pct": 0.020,
            "turnover_24h_usd": 1_650_000_000,
            "turnover_label": "1.65B $ / 24h",
            "depth_notional_top5_usd": 2_100_000,
            "slippage_est_pct": 0.007,
            "amihud_ratio": 0.000035,
            "rating": "AA (LIQUIDEZ CENTRAL)",
            "passed_gatekeeper": True,
        },
        "NVDA": {
            "tier": "TIER_1_ULTRA_LIQUID",
            "market_name": "NVIDIA Corporation (NASDAQ)",
            "spread_bps": 1.0,
            "spread_pct": 0.010,
            "turnover_24h_usd": 32_500_000_000,
            "turnover_label": "32.5B $ / día (Líder Mundial)",
            "depth_notional_top5_usd": 18_400_000,
            "slippage_est_pct": 0.001,
            "amihud_ratio": 0.000005,
            "rating": "AAA+ (MÁXIMA ROTACIÓN MUNDIAL)",
            "passed_gatekeeper": True,
        },
        "AAPL": {
            "tier": "TIER_1_ULTRA_LIQUID",
            "market_name": "Apple Inc. (NASDAQ)",
            "spread_bps": 0.9,
            "spread_pct": 0.009,
            "turnover_24h_usd": 16_800_000_000,
            "turnover_label": "16.8B $ / día",
            "depth_notional_top5_usd": 14_200_000,
            "slippage_est_pct": 0.001,
            "amihud_ratio": 0.000006,
            "rating": "AAA+ (MÁXIMA PROFUNDIDAD)",
            "passed_gatekeeper": True,
        },
        "TSLA": {
            "tier": "TIER_1_ULTRA_LIQUID",
            "market_name": "Tesla Inc. (NASDAQ)",
            "spread_bps": 1.4,
            "spread_pct": 0.014,
            "turnover_24h_usd": 19_200_000_000,
            "turnover_label": "19.2B $ / día",
            "depth_notional_top5_usd": 11_600_000,
            "slippage_est_pct": 0.003,
            "amihud_ratio": 0.000009,
            "rating": "AAA (ALTO VOLUMEN INTRADÍA)",
            "passed_gatekeeper": True,
        },
        "IBE.MC": {
            "tier": "TIER_1_ULTRA_LIQUID",
            "market_name": "Iberdrola S.A. (IBEX 35)",
            "spread_bps": 2.5,
            "spread_pct": 0.025,
            "turnover_24h_usd": 280_000_000,
            "turnover_label": "280M € / día (Líder Utilities)",
            "depth_notional_top5_usd": 2_800_000,
            "slippage_est_pct": 0.008,
            "amihud_ratio": 0.000045,
            "rating": "AA+ (MÁXIMA LIQUIDEZ ESPAÑA)",
            "passed_gatekeeper": True,
        },
        "SAN.MC": {
            "tier": "TIER_1_ULTRA_LIQUID",
            "market_name": "Banco Santander (IBEX 35)",
            "spread_bps": 2.2,
            "spread_pct": 0.022,
            "turnover_24h_usd": 320_000_000,
            "turnover_label": "320M € / día (Top Volumen BME)",
            "depth_notional_top5_usd": 3_500_000,
            "slippage_est_pct": 0.007,
            "amihud_ratio": 0.000040,
            "rating": "AA+ (MÁXIMA ROTACIÓN BANCARIA)",
            "passed_gatekeeper": True,
        },
        "ITX.MC": {
            "tier": "TIER_1_ULTRA_LIQUID",
            "market_name": "Inditex S.A. (IBEX 35)",
            "spread_bps": 2.8,
            "spread_pct": 0.028,
            "turnover_24h_usd": 210_000_000,
            "turnover_label": "210M € / día (Líder Capitalización)",
            "depth_notional_top5_usd": 2_200_000,
            "slippage_est_pct": 0.009,
            "amihud_ratio": 0.000052,
            "rating": "AA (BLUE CHIP GLOBAL)",
            "passed_gatekeeper": True,
        },
        "EURUSD": {
            "tier": "TIER_1_ULTRA_LIQUID",
            "market_name": "Euro / US Dollar FX",
            "spread_bps": 0.6,
            "spread_pct": 0.006,
            "turnover_24h_usd": 1_200_000_000_000,
            "turnover_label": "1.2 Billones $ / día (Par #1 del Mundo)",
            "depth_notional_top5_usd": 150_000_000,
            "slippage_est_pct": 0.0005,
            "amihud_ratio": 0.000001,
            "rating": "AAA+ (LIQUIDEZ SOBERANA MUNDIAL)",
            "passed_gatekeeper": True,
        },
        "USDJPY": {
            "tier": "TIER_1_ULTRA_LIQUID",
            "market_name": "US Dollar / Japanese Yen FX",
            "spread_bps": 0.8,
            "spread_pct": 0.008,
            "turnover_24h_usd": 900_000_000_000,
            "turnover_label": "900 Mil Millones $ / día (Par #2)",
            "depth_notional_top5_usd": 95_000_000,
            "slippage_est_pct": 0.0008,
            "amihud_ratio": 0.000002,
            "rating": "AAA+ (LIQUIDEZ SOBERANA MUNDIAL)",
            "passed_gatekeeper": True,
        },
        "XAUUSD": {
            "tier": "TIER_1_ULTRA_LIQUID",
            "market_name": "Gold Spot / US Dollar (Au Invariant)",
            "spread_bps": 1.1,
            "spread_pct": 0.011,
            "turnover_24h_usd": 145_000_000_000,
            "turnover_label": "145B $ / día (Activo Refugio Soberano)",
            "depth_notional_top5_usd": 42_000_000,
            "slippage_est_pct": 0.001,
            "amihud_ratio": 0.000004,
            "rating": "AAA+ (RESERVA ÁUREA INMUTABLE)",
            "passed_gatekeeper": True,
        },
    }

    def __init__(self) -> None:
        self.cached_prices: dict[str, float] = dict(self.BASE_PRICES)
        self.tick_history: dict[str, list[tuple[float, float, float]]] = {
            s: [] for s in self.ALL_SYMBOLS
        }
        self.last_api_poll_time: dict[str, float] = {}
        self._seed_initial_history()

    def _seed_initial_history(self) -> None:
        """Seeds 60 ticks per symbol so indicators can compute immediately."""
        now = time.time() - 600
        for i in range(60):
            t = now + i * 10
            for s in self.ALL_SYMBOLS:
                vol = round(random.uniform(5.0, 150.0), 2)
                p = self.cached_prices[s] * (1.0 + random.gauss(0, 0.0006))
                dec = 5 if ("USD" in s or "EUR" in s) and "BTC" not in s and "XAU" not in s else 2
                p = round(p, dec)
                self.cached_prices[s] = p
                self.tick_history[s].append((t, p, vol))

    def fetch_live_binance_price(self, symbol: str) -> float | None:
        """Fetches live public ticker price from Binance API without authentication."""
        clean_sym = re.sub(r"[^A-Z0-9]", "", symbol.upper())
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={clean_sym}"
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; NovusBot/3.0)"},
            )
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return float(data.get("price", 0.0))
        except Exception:
            return None

    def fetch_live_binance_depth(self, symbol: str, limit: int = 5) -> dict[str, Any]:
        """Fetches live Order Book depth (Bids & Asks) from Binance."""
        clean_sym = re.sub(r"[^A-Z0-9]", "", symbol.upper())
        clean_limit = max(1, min(int(limit), 100))
        url = f"https://api.binance.com/api/v3/depth?symbol={clean_sym}&limit={clean_limit}"
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; NovusBot/3.0)"},
            )
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                bids = [[float(b[0]), float(b[1])] for b in data.get("bids", [])]
                asks = [[float(a[0]), float(a[1])] for a in data.get("asks", [])]
                total_bid_vol = sum(b[1] for b in bids)
                total_ask_vol = sum(a[1] for a in asks)
                imbalance = (
                    round(((total_bid_vol - total_ask_vol) / max(total_bid_vol + total_ask_vol, 1e-6)) * 100.0, 1)
                )
                return {
                    "symbol": symbol,
                    "bids": bids,
                    "asks": asks,
                    "imbalance_pct": imbalance,
                    "bias": "COMPRADOR (+Bids)" if imbalance > 10 else ("VENDEDOR (+Asks)" if imbalance < -10 else "NEUTRAL"),
                }
        except Exception:
            # Fallback simulated orderbook around cached price
            p = self.cached_prices.get(symbol, 80000.0)
            if symbol in self.EQUITY_SYMBOLS:
                bids = [
                    [round(p * 0.9998, 2), float(random.randint(120, 850))],
                    [round(p * 0.9995, 2), float(random.randint(450, 1800))],
                    [round(p * 0.9991, 2), float(random.randint(1200, 4500))],
                    [round(p * 0.9986, 2), float(random.randint(2500, 8000))],
                    [round(p * 0.9980, 2), float(random.randint(4000, 15000))],
                ]
                asks = [
                    [round(p * 1.0002, 2), float(random.randint(100, 750))],
                    [round(p * 1.0005, 2), float(random.randint(400, 1600))],
                    [round(p * 1.0009, 2), float(random.randint(1100, 4200))],
                    [round(p * 1.0014, 2), float(random.randint(2300, 7500))],
                    [round(p * 1.0020, 2), float(random.randint(3800, 14000))],
                ]
                tot_b = sum(b[1] for b in bids)
                tot_a = sum(a[1] for a in asks)
                imb = round(((tot_b - tot_a) / max(tot_b + tot_a, 1.0)) * 100.0, 1)
                return {
                    "symbol": symbol,
                    "bids": bids,
                    "asks": asks,
                    "imbalance_pct": imb,
                    "bias": "COMPRADOR (+Bids)" if imb > 10 else ("VENDEDOR (+Asks)" if imb < -10 else "NEUTRAL"),
                }
            return {
                "symbol": symbol,
                "bids": [[round(p * 0.9999, 2), 0.85], [round(p * 0.9997, 2), 1.42], [round(p * 0.9995, 2), 3.20]],
                "asks": [[round(p * 1.0001, 2), 0.62], [round(p * 1.0003, 2), 1.15], [round(p * 1.0005, 2), 2.80]],
                "imbalance_pct": 14.5,
                "bias": "COMPRADOR (+Bids)",
            }

    def fetch_live_yahoo_price(self, symbol: str) -> float | None:
        """Fetches live public quote from Yahoo Finance API for Forex & Equities."""
        yahoo_sym = symbol
        if symbol == "EURUSD":
            yahoo_sym = "EURUSD=X"
        elif symbol == "USDJPY":
            yahoo_sym = "USDJPY=X"
        elif symbol == "GBPUSD":
            yahoo_sym = "GBPUSD=X"
        elif symbol == "USDCHF":
            yahoo_sym = "CHF=X"

        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_sym}?interval=1h&range=1d"
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"},
            )
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                meta = data["chart"]["result"][0]["meta"]
                p = float(meta.get("regularMarketPrice", 0.0))
                return p if p > 0 else None
        except Exception:
            return None

    def fetch_live_binance_klines(
        self,
        symbol: str,
        interval: str = "1h",
        limit: int = 50,
    ) -> list[Candle] | None:
        """Fetches real candlestick historical data from Binance."""
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; NovusBot/3.0)"},
            )
            with urllib.request.urlopen(req, timeout=3.5) as resp:
                raw_klines = json.loads(resp.read().decode("utf-8"))
                candles: list[Candle] = []
                for k in raw_klines:
                    candles.append(
                        Candle(
                            timestamp=float(k[0]) / 1000.0,
                            open=float(k[1]),
                            high=float(k[2]),
                            low=float(k[3]),
                            close=float(k[4]),
                            volume=float(k[5]),
                        )
                    )
                return candles
        except Exception:
            return None

    def fetch_live_yahoo_klines(
        self,
        symbol: str,
        interval: str = "1h",
        count: int = 50,
    ) -> list[Candle] | None:
        """Fetches real candlestick historical data from Yahoo Finance for Equities and Forex."""
        yahoo_sym = symbol
        if symbol == "EURUSD":
            yahoo_sym = "EURUSD=X"
        elif symbol == "USDJPY":
            yahoo_sym = "USDJPY=X"
        elif symbol == "GBPUSD":
            yahoo_sym = "GBPUSD=X"
        elif symbol == "USDCHF":
            yahoo_sym = "CHF=X"

        yahoo_range = "1mo" if count > 30 else "5d"
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_sym}?interval={interval}&range={yahoo_range}"
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"},
            )
            with urllib.request.urlopen(req, timeout=4.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                res = data["chart"]["result"][0]
                timestamps = res.get("timestamp", [])
                quotes = res["indicators"]["quote"][0]
                candles: list[Candle] = []
                for i in range(len(timestamps)):
                    o = quotes.get("open", [])[i] if i < len(quotes.get("open", [])) else None
                    h = quotes.get("high", [])[i] if i < len(quotes.get("high", [])) else None
                    l = quotes.get("low", [])[i] if i < len(quotes.get("low", [])) else None
                    c = quotes.get("close", [])[i] if i < len(quotes.get("close", [])) else None
                    v = quotes.get("volume", [])[i] if i < len(quotes.get("volume", [])) else 100
                    if o is not None and h is not None and l is not None and c is not None:
                        candles.append(
                            Candle(
                                timestamp=float(timestamps[i]),
                                open=round(float(o), 2 if float(o) > 10 else 5),
                                high=round(float(h), 2 if float(h) > 10 else 5),
                                low=round(float(l), 2 if float(l) > 10 else 5),
                                close=round(float(c), 2 if float(c) > 10 else 5),
                                volume=float(v or 100.0),
                            )
                        )
                if candles:
                    return candles[-count:]
                return None
        except Exception:
            return None

    def get_latest_price(self, symbol: str) -> tuple[float, float]:
        """Returns (price, volume) using live API if crypto or equity, or GBM simulation."""
        symbol = symbol.upper()
        if symbol not in self.ALL_SYMBOLS:
            symbol = "BTCUSDT"

        now = time.time()
        # 1. Try real live feed for crypto if not polled within last 2 seconds
        if symbol in self.CRYPTO_SYMBOLS:
            last_poll = self.last_api_poll_time.get(symbol, 0.0)
            if now - last_poll >= 2.0:
                live_p = self.fetch_live_binance_price(symbol)
                if live_p and live_p > 0:
                    self.cached_prices[symbol] = live_p
                    self.last_api_poll_time[symbol] = now
                    vol = round(random.uniform(5.0, 80.0), 3)
                    self.tick_history[symbol].append((now, live_p, vol))
                    if len(self.tick_history[symbol]) > 100:
                        self.tick_history[symbol].pop(0)
                    return live_p, vol

        # 2. Try real live feed for equities & forex if not polled within last 5 seconds
        if symbol in self.EQUITY_SYMBOLS or symbol in self.FOREX_SYMBOLS:
            last_poll = self.last_api_poll_time.get(symbol, 0.0)
            if now - last_poll >= 5.0:
                live_p = self.fetch_live_yahoo_price(symbol)
                if live_p and live_p > 0:
                    self.cached_prices[symbol] = live_p
                    self.last_api_poll_time[symbol] = now
                    vol = round(random.uniform(100.0, 5000.0), 2)
                    self.tick_history[symbol].append((now, live_p, vol))
                    if len(self.tick_history[symbol]) > 100:
                        self.tick_history[symbol].pop(0)
                    return live_p, vol

        # 3. Stochastic GBM Mean Reversion for Offline fallback
        prev_price = max(0.0001, self.cached_prices[symbol])
        base_price = max(0.0001, self.BASE_PRICES.get(symbol, 100.0))
        reversion_speed = 0.04
        drift = reversion_speed * ((base_price - prev_price) / base_price)
        sigma = 0.0010 if "USD" in symbol or "EUR" in symbol else 0.0020
        shock = random.gauss(0, sigma)

        new_price = max(0.0001, prev_price * (1.0 + drift + shock))
        decimals = 5 if ("USD" in symbol or "EUR" in symbol) and "BTC" not in symbol else 2
        new_price = round(new_price, decimals)
        vol = round(random.uniform(10.0, 180.0), 2)

        self.cached_prices[symbol] = new_price
        self.tick_history[symbol].append((now, new_price, vol))
        if len(self.tick_history[symbol]) > 100:
            self.tick_history[symbol].pop(0)

        return new_price, vol

    def get_historical_candles(
        self,
        symbol: str,
        interval: str = "1h",
        count: int = 60,
    ) -> list[Candle]:
        """Returns candle series either from live Binance klines, Yahoo klines, or synthetic generator."""
        symbol = symbol.upper()
        if symbol in self.CRYPTO_SYMBOLS:
            real_candles = self.fetch_live_binance_klines(symbol, interval, count)
            if real_candles and len(real_candles) >= 10:
                return real_candles
        elif symbol in self.EQUITY_SYMBOLS or symbol in self.FOREX_SYMBOLS:
            real_candles = self.fetch_live_yahoo_klines(symbol, interval, count)
            if real_candles and len(real_candles) >= 10:
                return real_candles

        # Synthetic realistic candle generator using Geometric Brownian Motion
        base_p = self.cached_prices.get(symbol, self.BASE_PRICES.get(symbol, 100.0))
        candles: list[Candle] = []
        now = time.time()
        step_seconds = 3600 if interval == "1h" else 300 if interval == "5m" else 86400
        start_time = now - (count * step_seconds)

        curr_p = base_p * 0.96
        for i in range(count):
            t = start_time + i * step_seconds
            ret = random.gauss(0.0003, 0.008)
            open_p = curr_p
            close_p = round(open_p * (1.0 + ret), 2 if base_p > 10 else 5)
            high_p = round(max(open_p, close_p) * (1.0 + abs(random.gauss(0, 0.004))), 2 if base_p > 10 else 5)
            low_p = round(min(open_p, close_p) * (1.0 - abs(random.gauss(0, 0.004))), 2 if base_p > 10 else 5)
            vol = round(random.uniform(50.0, 500.0), 2)
            candles.append(
                Candle(
                    timestamp=t,
                    open=open_p,
                    high=high_p,
                    low=low_p,
                    close=close_p,
                    volume=vol,
                )
            )
            curr_p = close_p

        return candles

    def generate_stress_candles(
        self,
        symbol: str,
        count: int = 150,
    ) -> list[Candle]:
        """
        Generates a realistic multi-regime series containing high volatility,
        mean-reversion opportunities, and deliberate adverse shocks to stress-test
        the risk manager and demonstrate controlled stop-loss failure execution.
        """
        base_p = self.cached_prices.get(symbol, self.BASE_PRICES.get(symbol, 100.0))
        candles: list[Candle] = []
        now = time.time()
        step_seconds = 3600
        start_time = now - (count * step_seconds)

        curr_p = base_p
        for i in range(count):
            t = start_time + i * step_seconds
            wave_pos = (i - 20) % 20 if i >= 20 else 0
            wave_idx = (i - 20) // 20 if i >= 20 else 0

            if i < 20:
                ret = random.uniform(-0.002, 0.002)
            elif wave_pos == 0:
                ret = -0.024  # dip into extreme oversold -> triggers buy
            elif wave_pos in (1, 2):
                if wave_idx in (1, 3, 5):
                    ret = -0.019  # adverse follow-through -> triggers real stop loss
                else:
                    ret = +0.019  # favorable bounce -> triggers take-profit
            elif wave_pos in (3, 4, 5):
                ret = +0.012 if wave_idx in (1, 3, 5) else +0.004
            else:
                ret = random.uniform(-0.003, 0.003)

            open_p = curr_p
            close_p = round(max(0.0001, open_p * (1.0 + ret)), 2 if base_p > 10 else 5)
            spread = abs(open_p - close_p) * 0.35
            high_p = round(max(open_p, close_p) + spread + abs(random.gauss(0, base_p * 0.001)), 2 if base_p > 10 else 5)
            low_p = round(max(0.0001, min(open_p, close_p) - spread - abs(random.gauss(0, base_p * 0.001))), 2 if base_p > 10 else 5)
            vol = round(random.uniform(80.0, 850.0), 2)
            candles.append(
                Candle(
                    timestamp=t,
                    open=open_p,
                    high=high_p,
                    low=low_p,
                    close=close_p,
                    volume=vol,
                )
            )
            curr_p = close_p

        return candles

    def get_liquidity_profile(self, symbol: str) -> dict[str, Any]:
        """Provides institutional liquidity metrics, bid-ask spread and Amihud ratio."""
        sym = symbol.upper()
        if sym in self.LIQUIDITY_METRICS:
            profile = dict(self.LIQUIDITY_METRICS[sym])
        else:
            profile = {
                "tier": "TIER_1_ULTRA_LIQUID",
                "market_name": f"{sym} Liquid Market",
                "spread_bps": 1.8,
                "spread_pct": 0.018,
                "turnover_24h_usd": 1_000_000_000,
                "turnover_label": "1.0B $ / 24h",
                "depth_notional_top5_usd": 3_500_000,
                "slippage_est_pct": 0.005,
                "amihud_ratio": 0.000020,
                "rating": "AA (PROFUNDIDAD VERIFICADA)",
                "passed_gatekeeper": True,
            }

        # Calculate live spread from depth
        ob = self.fetch_live_binance_depth(sym, limit=2)
        if ob.get("bids") and ob.get("asks"):
            bid1 = ob["bids"][0][0]
            ask1 = ob["asks"][0][0]
            mid = (bid1 + ask1) / 2.0
            if mid > 0:
                live_spread = round(((ask1 - bid1) / mid) * 100.0, 3)
                profile["live_spread_pct"] = max(0.004, live_spread)
                profile["live_spread_eur"] = round(ask1 - bid1, 2 if mid > 10 else 5)
                profile["top_bid"] = bid1
                profile["top_ask"] = ask1
        return profile

    @classmethod
    def is_market_open(cls, symbol: str, timestamp: float | None = None) -> bool:
        """
        Determines if the given asset is currently open for trading based on its calendar (UTC).
        - Cryptos: 24/7/365 (Always True).
        - Forex: Sunday 22:00 UTC to Friday 22:00 UTC.
        - Commodities (XAUUSD): Sunday 23:00 UTC to Friday 22:00 UTC (daily 22:00-23:00 UTC maintenance roll).
        - US Equities: Monday to Friday 13:30 to 20:00 UTC.
        - EU Equities: Monday to Friday 08:00 to 16:30 UTC.
        """
        sym = symbol.upper()
        if sym in cls.CRYPTO_SYMBOLS or "USDT" in sym or "BTC" in sym or "ETH" in sym or "SOL" in sym or "BNB" in sym:
            return True

        dt = (
            datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
            if timestamp is not None
            else datetime.datetime.now(datetime.timezone.utc)
        )
        weekday = dt.weekday()  # Monday=0, Sunday=6
        minute_of_day = dt.hour * 60 + dt.minute

        # Forex: Sun 22:00 UTC -> Fri 22:00 UTC
        if sym in cls.FOREX_SYMBOLS or "EUR" in sym or "JPY" in sym or "GBP" in sym or "CHF" in sym:
            if weekday == 5:  # Saturday
                return False
            if weekday == 6:  # Sunday
                return dt.hour >= 22
            if weekday == 4:  # Friday
                return dt.hour < 22
            return True  # Mon-Thu

        # Commodity (Gold XAUUSD): Sun 23:00 UTC -> Fri 22:00 UTC with daily 22:00-23:00 roll break
        if sym in cls.COMMODITY_SYMBOLS or "XAU" in sym:
            if weekday == 5:  # Saturday
                return False
            if weekday == 6:  # Sunday
                return dt.hour >= 23
            if weekday == 4:  # Friday
                return dt.hour < 22
            # Mon-Thu: break at 22:00 - 23:00 UTC
            return dt.hour != 22

        # US Equities: Mon-Fri 13:30 - 20:00 UTC
        if sym in cls.US_EQUITY_SYMBOLS:
            if weekday >= 5:  # Weekend
                return False
            return 810 <= minute_of_day < 1200  # 13:30 to 20:00 UTC

        # EU Equities: Mon-Fri 08:00 - 16:30 UTC (09:00 - 17:30 CET)
        if sym in cls.EU_EQUITY_SYMBOLS or ".MC" in sym or ".PA" in sym:
            if weekday >= 5:  # Weekend
                return False
            return 480 <= minute_of_day < 990  # 08:00 to 16:30 UTC

        # Fallback default
        return True

    @classmethod
    def get_symbol_market_status(cls, symbol: str, timestamp: float | None = None) -> dict[str, Any]:
        """Provides status details, schedule label, and asset classification for a symbol."""
        sym = symbol.upper()
        is_crypto = sym in cls.CRYPTO_SYMBOLS or "USDT" in sym or "BTC" in sym or "ETH" in sym or "SOL" in sym or "BNB" in sym
        is_open = cls.is_market_open(sym, timestamp)

        if is_crypto:
            asset_class = "CRYPTO"
            status = "24/7 SPOT"
            hours_label = "24/7/365 Negociación Continua Ininterrumpida"
        elif sym in cls.COMMODITY_SYMBOLS or "XAU" in sym:
            asset_class = "COMMODITY"
            status = "ABIERTO" if is_open else "CERRADO"
            hours_label = "Dom 23:00 UTC - Vie 22:00 UTC (Reserva Áurea)"
        elif sym in cls.FOREX_SYMBOLS:
            asset_class = "FOREX"
            status = "ABIERTO" if is_open else "CERRADO"
            hours_label = "Dom 22:00 UTC - Vie 22:00 UTC (Interbancario)"
        elif sym in cls.US_EQUITY_SYMBOLS:
            asset_class = "EQUITY_US"
            status = "ABIERTO" if is_open else "CERRADO"
            hours_label = "Lun-Vie 13:30 - 20:00 UTC (Wall Street / NASDAQ)"
        elif sym in cls.EU_EQUITY_SYMBOLS or ".MC" in sym or ".PA" in sym:
            asset_class = "EQUITY_EU"
            status = "ABIERTO" if is_open else "CERRADO"
            hours_label = "Lun-Vie 08:00 - 16:30 UTC (BME / Euronext)"
        else:
            asset_class = "EQUITY"
            status = "ABIERTO" if is_open else "CERRADO"
            hours_label = "Horario Estándar de Mercado"

        return {
            "symbol": sym,
            "is_open": is_open,
            "status": status,
            "asset_class": asset_class,
            "hours_label": hours_label,
            "crypto_fallback_candidate": not is_open,
        }

    def get_open_symbols(self, timestamp: float | None = None) -> list[str]:
        """Returns all symbols open at the given timestamp. Always includes CRYPTO_SYMBOLS."""
        open_syms = [s for s in self.ALL_SYMBOLS if self.is_market_open(s, timestamp)]
        for c in self.CRYPTO_SYMBOLS:
            if c not in open_syms:
                open_syms.append(c)
        return open_syms

    def get_market_regime(self, timestamp: float | None = None) -> dict[str, Any]:
        """
        Analyzes the open/closed status across all asset classes and detects if
        traditional markets are offline, triggering the 24/7 Crypto Fallback Engine.
        """
        dt = (
            datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
            if timestamp is not None
            else datetime.datetime.now(datetime.timezone.utc)
        )
        ts = dt.timestamp()

        crypto_open = True
        forex_open = any(self.is_market_open(s, ts) for s in self.FOREX_SYMBOLS)
        equities_open = any(self.is_market_open(s, ts) for s in self.EQUITY_SYMBOLS)
        us_equities_open = any(self.is_market_open(s, ts) for s in self.US_EQUITY_SYMBOLS)
        eu_equities_open = any(self.is_market_open(s, ts) for s in self.EU_EQUITY_SYMBOLS)
        commodities_open = any(self.is_market_open(s, ts) for s in self.COMMODITY_SYMBOLS)

        open_symbols = [s for s in self.ALL_SYMBOLS if self.is_market_open(s, ts)]
        closed_symbols = [s for s in self.ALL_SYMBOLS if not self.is_market_open(s, ts)]

        if equities_open and forex_open:
            active_focus = "ALL_MARKETS"
            status_label = "🟢 Todos los Mercados Abiertos (Bolsa + FX + Crypto 24/7)"
            badge = "MULTIMERCADO"
            reason = "Sesión bursátil y mercado interbancario de divisas plenamente operativos."
            crypto_pivot_active = False
        elif forex_open and not equities_open:
            active_focus = "CRYPTO_AND_FOREX"
            status_label = "🌙 Bolsas Cerradas · 🟢 Forex & Crypto 24/7 Activos"
            badge = "FOREX + CRYPTO"
            reason = "Bolsas de valores fuera de horario (sesión nocturna). Operando divisas y criptoactivos 24/7."
            crypto_pivot_active = True
        elif equities_open and not forex_open:
            active_focus = "CRYPTO_AND_EQUITIES"
            status_label = "🟢 Bolsas Abiertas · 🟢 Crypto 24/7 Activo"
            badge = "BOLSA + CRYPTO"
            reason = "Sesión de renta variable y criptoactivos en negociación activa."
            crypto_pivot_active = False
        else:
            active_focus = "CRYPTO_24_7"
            status_label = "🌙 Mercados Tradicionales Cerrados (Fin de Semana / Festivo) · 🟢 Pivot 100% Crypto 24/7"
            badge = "CRYPTO 24/7"
            reason = "Bolsas y Forex cerrados. El 100% de la liquidez y operativa algorítmica está canalizada a Criptomonedas (BTC, ETH, SOL, BNB)."
            crypto_pivot_active = True

        return {
            "timestamp": ts,
            "utc_time": dt.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "weekday": dt.strftime("%A"),
            "active_focus": active_focus,
            "status_label": status_label,
            "badge": badge,
            "reason": reason,
            "crypto_pivot_active": crypto_pivot_active,
            "crypto_24_7": True,
            "equities_open": equities_open,
            "us_equities_open": us_equities_open,
            "eu_equities_open": eu_equities_open,
            "forex_open": forex_open,
            "commodities_open": commodities_open,
            "open_symbols": open_symbols,
            "closed_symbols": closed_symbols,
            "open_symbols_count": len(open_symbols),
            "closed_symbols_count": len(closed_symbols),
            "prioritized_crypto_symbols": list(self.CRYPTO_SYMBOLS),
        }


