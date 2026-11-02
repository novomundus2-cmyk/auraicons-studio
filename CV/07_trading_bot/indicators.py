"""Vectorized technical analysis and quantitative indicators."""

from __future__ import annotations

import math
import numpy as np


class Indicators:
    @staticmethod
    def sma(prices: list[float] | np.ndarray, period: int) -> np.ndarray:
        arr = np.asarray(prices, dtype=np.float64)
        if len(arr) < period:
            return np.full_like(arr, np.nan)
        weights = np.ones(period) / period
        res = np.convolve(arr, weights, mode="valid")
        prefix = np.full(period - 1, np.nan)
        return np.concatenate((prefix, res))

    @staticmethod
    def ema(prices: list[float] | np.ndarray, period: int) -> np.ndarray:
        arr = np.asarray(prices, dtype=np.float64)
        n = len(arr)
        if n == 0:
            return np.array([])
        if n < period:
            return np.full_like(arr, np.nan)

        alpha = 2.0 / (period + 1.0)
        res = np.empty(n, dtype=np.float64)
        res[: period - 1] = np.nan
        res[period - 1] = np.mean(arr[:period])
        for i in range(period, n):
            res[i] = alpha * arr[i] + (1.0 - alpha) * res[i - 1]
        return res

    @staticmethod
    def rsi(prices: list[float] | np.ndarray, period: int = 14) -> np.ndarray:
        arr = np.asarray(prices, dtype=np.float64)
        n = len(arr)
        if n <= period:
            return np.full(n, 50.0)

        deltas = np.diff(arr)
        gains = np.where(deltas > 0, deltas, 0.0)
        losses = np.where(deltas < 0, -deltas, 0.0)

        res = np.empty(n, dtype=np.float64)
        res[:period] = np.nan

        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])

        if avg_loss == 0.0:
            res[period] = 100.0 if avg_gain > 0 else 50.0
        else:
            rs = avg_gain / avg_loss
            res[period] = 100.0 - (100.0 / (1.0 + rs))

        # Wilder's smoothing
        for i in range(period, len(deltas)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            if avg_loss == 0.0:
                res[i + 1] = 100.0 if avg_gain > 0 else 50.0
            else:
                rs = avg_gain / avg_loss
                res[i + 1] = 100.0 - (100.0 / (1.0 + rs))

        return np.nan_to_num(res, nan=50.0)

    @staticmethod
    def vwap(
        prices: list[float] | np.ndarray,
        volumes: list[float] | np.ndarray,
    ) -> float:
        p = np.asarray(prices, dtype=np.float64)
        v = np.asarray(volumes, dtype=np.float64)
        total_vol = np.sum(v)
        if total_vol <= 0:
            return float(p[-1]) if len(p) > 0 else 0.0
        return float(np.sum(p * v) / total_vol)

    @staticmethod
    def robust_mad(prices: list[float] | np.ndarray) -> float:
        """Median Absolute Deviation (MAD) scaled by 1.4826 for normal consistency."""
        arr = np.asarray(prices, dtype=np.float64)
        if len(arr) < 2:
            return 0.0
        med = float(np.median(arr))
        deviations = np.abs(arr - med)
        mad = float(np.median(deviations))
        return float(mad * 1.4826)

    @staticmethod
    def bollinger_bands(
        prices: list[float] | np.ndarray,
        period: int = 20,
        num_std: float = 2.0,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Calculates Upper Band, Middle Band (SMA), Lower Band."""
        arr = np.asarray(prices, dtype=np.float64)
        n = len(arr)
        if n < period:
            return arr.copy(), arr.copy(), arr.copy()

        mid = Indicators.sma(arr, period)
        upper = np.copy(mid)
        lower = np.copy(mid)

        for i in range(period - 1, n):
            std = float(np.std(arr[i - period + 1 : i + 1], ddof=1))
            upper[i] = mid[i] + num_std * std
            lower[i] = mid[i] - num_std * std

        return upper, mid, lower

    @staticmethod
    def atr(
        highs: list[float] | np.ndarray,
        lows: list[float] | np.ndarray,
        closes: list[float] | np.ndarray,
        period: int = 14,
    ) -> np.ndarray:
        h = np.asarray(highs, dtype=np.float64)
        l = np.asarray(lows, dtype=np.float64)
        c = np.asarray(closes, dtype=np.float64)
        n = len(c)
        if n < 2:
            return np.zeros(n)

        tr = np.empty(n, dtype=np.float64)
        tr[0] = h[0] - l[0]
        for i in range(1, n):
            hl = h[i] - l[i]
            hc = abs(h[i] - c[i - 1])
            lc = abs(l[i] - c[i - 1])
            tr[i] = max(hl, hc, lc)

        if n <= period:
            return np.full(n, np.mean(tr))

        atr_arr = np.empty(n, dtype=np.float64)
        atr_arr[:period] = np.nan
        atr_arr[period - 1] = np.mean(tr[:period])
        for i in range(period, n):
            atr_arr[i] = (atr_arr[i - 1] * (period - 1) + tr[i]) / period

        return np.nan_to_num(atr_arr, nan=atr_arr[period - 1] if period - 1 < n else tr[0])

    @staticmethod
    def z_score(value: float, mean: float, std: float) -> float:
        if std <= 1e-12:
            return 0.0
        return float((value - mean) / std)
