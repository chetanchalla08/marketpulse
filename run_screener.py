"""
Week 2 milestone script: fetches data, computes indicators, STORES a
snapshot in the database, evaluates screening rules, and stores + prints
any triggered signals.

Run with: python run_screener.py
"""

from src.data_fetcher import fetch_daily_bars
from src.indicators import add_all_indicators
from src.screener import evaluate_rules
from src.db import get_session, IndicatorSnapshot, Signal, create_tables

WATCHLIST = ["AAPL", "TSLA", "NVDA", "SPY", "MSFT"]


def store_snapshot(session, symbol: str, latest_row) -> None:
    # Cast numpy types (np.float64, etc.) to plain Python floats — the
    # database driver doesn't know how to insert numpy scalar types directly.
    snapshot = IndicatorSnapshot(
        symbol=symbol,
        timestamp=latest_row.name,  # the row's index value is the timestamp
        close=float(latest_row["close"]),
        volume=float(latest_row["volume"]),
        rsi=float(latest_row["rsi"]),
        macd=float(latest_row["macd"]),
        macd_signal=float(latest_row["macd_signal"]),
        macd_hist=float(latest_row["macd_hist"]),
        vwap=float(latest_row["vwap"]),
    )
    session.add(snapshot)


def store_signals(session, triggered_signals: list[dict]) -> None:
    for sig in triggered_signals:
        session.add(Signal(**sig))


def run_screener():
    # Make sure tables exist (safe to call every run — it's a no-op if they already do)
    create_tables()

    session = get_session()
    total_signals = 0

    print(f"Screening {WATCHLIST}...\n")

    for symbol in WATCHLIST:
        try:
            df = fetch_daily_bars(symbol, lookback_days=100)
            enriched = add_all_indicators(df)
            latest = enriched.iloc[-1]

            # Save this run's indicator values to the DB (builds history for backtesting)
            store_snapshot(session, symbol, latest)

            # Check all rules
            triggered = evaluate_rules(enriched, symbol)
            store_signals(session, triggered)

            if triggered:
                print(f"{symbol}: {len(triggered)} signal(s) triggered")
                for sig in triggered:
                    print(f"   [{sig['rule_name']}] {sig['details']}")
            else:
                print(f"{symbol}: no signals (RSI={latest['rsi']:.1f}, close vs VWAP={'above' if latest['close'] > latest['vwap'] else 'below'})")

            total_signals += len(triggered)

        except Exception as e:
            print(f"  [ERROR] {symbol}: {e}")

    session.commit()
    session.close()

    print(f"\nDone. {total_signals} total signal(s) stored to the database this run.")


if __name__ == "__main__":
    run_screener()
