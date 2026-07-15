"""
Backtesting engine: replays the existing screening rules against historical
data to answer the question "when this rule triggered in the past, what
actually happened to price afterward?"

Key design point: this does NOT recompute indicators separately for each
historical day. Since RSI/MACD/VWAP are all "causal" (each day's value only
depends on that day and earlier days -- see indicators.py), we can compute
indicators ONCE over the full history, then walk through it day by day,
looking only at data up to and including that day. This avoids any lookahead
bias while staying fast.
"""

import pandas as pd
from src.screener import RULES


def backtest_rule(enriched_df: pd.DataFrame, rule_name: str, rule_fn, horizons=(1, 3, 5)) -> list[dict]:
    """
    Walks through enriched_df day by day, checking one rule at each point.
    Whenever it triggers, records the forward return over each horizon
    (in trading days). Returns a list of trigger events with their outcomes.
    """
    results = []
    n = len(enriched_df)
    max_horizon = max(horizons)

    # Start after enough bars for indicators to be "warmed up" (no NaNs),
    # stop early enough that every trigger has full forward data to check.
    start = 30
    end = n - max_horizon

    for i in range(start, end):
        latest = enriched_df.iloc[i]
        prior = enriched_df.iloc[i - 1]

        if rule_fn.__code__.co_argcount == 1:
            triggered, reason = rule_fn(latest)
        else:
            triggered, reason = rule_fn(latest, prior)

        if not triggered:
            continue

        entry_price = latest["close"]
        entry_date = enriched_df.index[i]

        outcome = {"rule_name": rule_name, "date": entry_date, "entry_price": entry_price}
        for h in horizons:
            future_price = enriched_df.iloc[i + h]["close"]
            forward_return_pct = (future_price - entry_price) / entry_price * 100
            outcome[f"return_{h}d_pct"] = forward_return_pct

        results.append(outcome)

    return results


def backtest_symbol(enriched_df: pd.DataFrame, symbol: str, horizons=(1, 3, 5)) -> list[dict]:
    """Runs every registered rule's backtest for one symbol."""
    all_results = []
    for rule_name, rule_fn in RULES.items():
        events = backtest_rule(enriched_df, rule_name, rule_fn, horizons)
        for event in events:
            event["symbol"] = symbol
        all_results.extend(events)
    return all_results


def summarize_results(results: list[dict], horizons=(1, 3, 5)) -> pd.DataFrame:
    """
    Aggregates raw trigger events into per-rule summary stats:
    trigger count, win rate, and average return at each horizon.
    """
    if not results:
        return pd.DataFrame()

    df = pd.DataFrame(results)
    summary_rows = []

    for rule_name, group in df.groupby("rule_name"):
        row = {"rule_name": rule_name, "trigger_count": len(group)}
        for h in horizons:
            col = f"return_{h}d_pct"
            row[f"win_rate_{h}d"] = (group[col] > 0).mean() * 100
            row[f"avg_return_{h}d_pct"] = group[col].mean()
        summary_rows.append(row)

    return pd.DataFrame(summary_rows)
