"""
Technical indicator calculations, implemented from their underlying formulas
(not imported from a black-box TA library) so the logic is fully understood
and defensible in an interview setting.

Expects a pandas DataFrame with columns: ['open', 'high', 'low', 'close', 'volume']
indexed by timestamp, ascending chronological order.
"""

import pandas as pd
import numpy as np


def compute_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Relative Strength Index.
    RSI = 100 - (100 / (1 + RS))
    RS  = average gain / average loss over the lookback period (Wilder's smoothing)
    """
    delta = df["close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    # Wilder's smoothing (equivalent to an EMA with alpha = 1/period)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    # Handle the edge case where avg_loss is 0 (no losses in window -> RSI = 100)
    rsi = rsi.where(avg_loss != 0, 100)
    return rsi.rename("rsi")


def compute_macd(
    df: pd.DataFrame,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
) -> pd.DataFrame:
    """
    MACD = EMA(fast) - EMA(slow)
    Signal line = EMA(MACD, signal_period)
    Histogram = MACD - Signal
    """
    ema_fast = df["close"].ewm(span=fast_period, adjust=False).mean()
    ema_slow = df["close"].ewm(span=slow_period, adjust=False).mean()

    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    histogram = macd_line - signal_line

    return pd.DataFrame(
        {
            "macd": macd_line,
            "macd_signal": signal_line,
            "macd_hist": histogram,
        }
    )


def compute_vwap(df: pd.DataFrame) -> pd.Series:
    """
    Volume Weighted Average Price, reset each trading day.
    VWAP = cumulative(typical_price * volume) / cumulative(volume)
    typical_price = (high + low + close) / 3

    Assumes df.index is a DatetimeIndex so we can group by calendar day.
    """
    typical_price = (df["high"] + df["low"] + df["close"]) / 3
    tp_vol = typical_price * df["volume"]

    day = df.index.date
    cum_tp_vol = tp_vol.groupby(day).cumsum()
    cum_vol = df["volume"].groupby(day).cumsum()

    vwap = cum_tp_vol / cum_vol
    return vwap.rename("vwap")


def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Convenience wrapper: returns the original df with RSI, MACD, and VWAP columns added."""
    out = df.copy()
    out["rsi"] = compute_rsi(out)
    macd_df = compute_macd(out)
    out = out.join(macd_df)
    out["vwap"] = compute_vwap(out)
    return out
