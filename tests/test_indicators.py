"""
Sanity checks for indicators.py using synthetic data with a known shape,
so you can trust the math before plugging in real market data.

Run with: python -m pytest tests/test_indicators.py -v
(or just: python tests/test_indicators.py)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pandas as pd
from src.indicators import compute_rsi, compute_macd, compute_vwap, add_all_indicators


def make_synthetic_df(n=100, seed=42):
    """Generate a fake but realistic-looking OHLCV series for testing."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2026-01-01 09:30", periods=n, freq="1min")

    price = 100 + np.cumsum(rng.normal(0, 0.3, n))
    close = price
    open_ = close + rng.normal(0, 0.1, n)
    high = np.maximum(open_, close) + np.abs(rng.normal(0, 0.2, n))
    low = np.minimum(open_, close) - np.abs(rng.normal(0, 0.2, n))
    volume = rng.integers(1000, 5000, n)

    df = pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": volume},
        index=dates,
    )
    return df


def test_rsi_bounds():
    df = make_synthetic_df()
    rsi = compute_rsi(df)
    valid = rsi.dropna()
    assert (valid >= 0).all() and (valid <= 100).all(), "RSI must stay within [0, 100]"
    print("test_rsi_bounds passed")


def test_rsi_all_gains_is_100():
    """If price only ever goes up, RSI should hit 100."""
    dates = pd.date_range("2026-01-01", periods=20, freq="D")
    close = np.arange(100, 120)  # strictly increasing
    df = pd.DataFrame(
        {"open": close, "high": close, "low": close, "close": close, "volume": [1000] * 20},
        index=dates,
    )
    rsi = compute_rsi(df, period=14)
    assert rsi.iloc[-1] == 100, f"Expected RSI 100 for all-gains series, got {rsi.iloc[-1]}"
    print("test_rsi_all_gains_is_100 passed")


def test_macd_shape():
    df = make_synthetic_df()
    macd_df = compute_macd(df)
    assert list(macd_df.columns) == ["macd", "macd_signal", "macd_hist"]
    # histogram should equal macd - signal
    diff = (macd_df["macd"] - macd_df["macd_signal"] - macd_df["macd_hist"]).abs()
    assert (diff < 1e-9).all(), "macd_hist should equal macd - macd_signal"
    print("test_macd_shape passed")


def test_vwap_resets_daily():
    """VWAP should reset at the start of each new calendar day."""
    dates = pd.date_range("2026-01-01 09:30", periods=5, freq="1min").append(
        pd.date_range("2026-01-02 09:30", periods=5, freq="1min")
    )
    close = [100, 101, 102, 103, 104, 200, 201, 202, 203, 204]
    df = pd.DataFrame(
        {
            "open": close,
            "high": close,
            "low": close,
            "close": close,
            "volume": [1000] * 10,
        },
        index=dates,
    )
    vwap = compute_vwap(df)
    # First value of day 2 should be close to day 2's typical price, not influenced by day 1
    assert abs(vwap.iloc[5] - 200) < 1, f"VWAP should reset on new day, got {vwap.iloc[5]}"
    print("test_vwap_resets_daily passed")


def test_add_all_indicators_runs():
    df = make_synthetic_df()
    out = add_all_indicators(df)
    for col in ["rsi", "macd", "macd_signal", "macd_hist", "vwap"]:
        assert col in out.columns
    print("test_add_all_indicators_runs passed")


if __name__ == "__main__":
    test_rsi_bounds()
    test_rsi_all_gains_is_100()
    test_macd_shape()
    test_vwap_resets_daily()
    test_add_all_indicators_runs()
    print("\nAll indicator sanity checks passed.")
