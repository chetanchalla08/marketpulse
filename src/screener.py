"""
The screening rule engine: takes a DataFrame of indicator values (from
indicators.py) and evaluates it against defined trading setups.

Each rule is just a Python function that takes the latest row of indicators
and returns True/False plus a human-readable reason. This design makes it
easy to add new rules later without touching the rest of the pipeline.
"""

import pandas as pd


def rule_oversold_reclaim_vwap(latest: pd.Series) -> tuple[bool, str]:
    """
    Classic mean-reversion setup: RSI shows the stock was recently oversold,
    AND price has reclaimed VWAP (a sign buyers are stepping back in).
    """
    triggered = latest["rsi"] < 35 and latest["close"] > latest["vwap"]
    reason = (
        f"RSI={latest['rsi']:.1f} (oversold) and close ${latest['close']:.2f} "
        f"is above VWAP ${latest['vwap']:.2f}"
    )
    return triggered, reason


def rule_macd_bullish_crossover(latest: pd.Series, prior: pd.Series) -> tuple[bool, str]:
    """
    MACD line crosses above the signal line between the prior bar and the
    latest bar — a classic momentum-shift signal.
    """
    crossed_up = prior["macd"] <= prior["macd_signal"] and latest["macd"] > latest["macd_signal"]
    reason = (
        f"MACD crossed above signal line "
        f"({prior['macd']:.3f}->{latest['macd']:.3f} vs signal {latest['macd_signal']:.3f})"
    )
    return crossed_up, reason


def rule_overbought_warning(latest: pd.Series) -> tuple[bool, str]:
    """
    Simple overextension warning: RSI very high while price is well above VWAP.
    Not necessarily a "sell", just a flag worth knowing about.
    """
    triggered = latest["rsi"] > 70 and latest["close"] > latest["vwap"] * 1.01
    reason = (
        f"RSI={latest['rsi']:.1f} (overbought), close ${latest['close']:.2f} "
        f"is >1% above VWAP ${latest['vwap']:.2f}"
    )
    return triggered, reason


# Registry of all active rules. Add new functions above, then register them here.
RULES = {
    "oversold_reclaim_vwap": rule_oversold_reclaim_vwap,
    "macd_bullish_crossover": rule_macd_bullish_crossover,
    "overbought_warning": rule_overbought_warning,
}


def evaluate_rules(enriched_df: pd.DataFrame, symbol: str) -> list[dict]:
    """
    Runs every registered rule against the most recent data for a symbol.
    Returns a list of dicts, one per triggered rule, ready to store in the
    Signal table.
    """
    if len(enriched_df) < 2:
        return []  # not enough history to check crossovers

    latest = enriched_df.iloc[-1]
    prior = enriched_df.iloc[-2]
    triggered_signals = []

    for rule_name, rule_fn in RULES.items():
        # Rules that only need the latest row take 1 arg; crossover rules take 2.
        if rule_fn.__code__.co_argcount == 1:
            triggered, reason = rule_fn(latest)
        else:
            triggered, reason = rule_fn(latest, prior)

        if triggered:
            triggered_signals.append(
                {
                    "symbol": symbol,
                    "timestamp": enriched_df.index[-1],
                    "rule_name": rule_name,
                    "close_at_signal": float(latest["close"]),  # cast numpy -> plain float for DB insert
                    "details": reason,
                }
            )

    return triggered_signals
