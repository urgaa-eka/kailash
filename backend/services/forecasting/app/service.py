"""Forecasting service — univariate time-series forecasting.

Uses a lightweight Holt-Winters style additive model (no heavy deps)
as the baseline. Prophet / NeuralProphet / XGBoost can be plugged in
as alternate providers.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from backend.shared import ValidationError


@dataclass
class ForecastResult:
    horizon: int
    yhat: list[float]
    yhat_lower: list[float]
    yhat_upper: list[float]
    method: str


def _ema(series: np.ndarray, alpha: float) -> np.ndarray:
    out = np.empty_like(series, dtype=float)
    out[0] = series[0]
    for i in range(1, len(series)):
        out[i] = alpha * series[i] + (1 - alpha) * out[i - 1]
    return out


def forecast(y: Sequence[float], horizon: int, *, season: int = 0) -> ForecastResult:
    if horizon <= 0 or horizon > 365:
        raise ValidationError("horizon must be in 1..365")
    if not y or len(y) < 3:
        raise ValidationError("need at least 3 observations")

    arr = np.asarray(y, dtype=float)
    level = _ema(arr, 0.4)[-1]
    # Trend via simple linear fit on last window.
    win = min(30, len(arr))
    xs = np.arange(win)
    slope = float(np.polyfit(xs, arr[-win:], 1)[0])

    seasonal_cycle: np.ndarray | None = None
    if season and season > 1 and len(arr) >= 2 * season:
        by_phase: list[float] = []
        for i in range(season):
            idxs = np.arange(i, len(arr), season)
            by_phase.append(float(arr[idxs].mean()))
        seasonal_cycle = np.asarray(by_phase) - float(arr.mean())

    residual = float(np.std(arr - _ema(arr, 0.4)))
    yhat = []
    for h in range(1, horizon + 1):
        val = level + slope * h
        if seasonal_cycle is not None:
            val += seasonal_cycle[(len(arr) + h - 1) % len(seasonal_cycle)]
        yhat.append(float(val))
    yhat_arr = np.asarray(yhat)
    return ForecastResult(
        horizon=horizon,
        yhat=yhat_arr.tolist(),
        yhat_lower=(yhat_arr - 1.96 * residual).tolist(),
        yhat_upper=(yhat_arr + 1.96 * residual).tolist(),
        method=f"ema+trend{'+seasonal' if seasonal_cycle is not None else ''}",
    )
