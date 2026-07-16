"""
Fetches data, computes indicators, STORES a snapshot in the database,
evaluates screening rules, and stores + alerts on any triggered signals.

Runs across the full S&P 500 by default. Uses batched API requests
(see fetch_multiple_symbols in data_fetcher.py) so this stays fast and
avoids hitting Alpaca's rate limits, even at 500-ticker scale.

Run with: python run_screener.py
"""

from src.data_fetcher import fetch_multiple_symbols
from src.indicators import add_all_indicators
from src.screener import evaluate_rules
from src.db import get_session, IndicatorSnapshot, Signal, create_tables
from src.alerts import send_discord_alert
from src.sp500 import fetch_sp500_tickers

# Set USE_SP500 = False to fall back to a small manual watchlist for quick local testing.
USE_SP500 = True
MANUAL_WATCHLIST = ["AAPL", "TSLA", "NVDA", "SPY", "MSFT"]


def store_snapshot(session, symbol: str, latest_row) -> None:
    # Cast numpy types (np.float64, etc.) to plain Python floats — the
    # database driver doesn't know how to insert numpy scalar types directly.
    snapshot = IndicatorSnapshot(
        symbol=symbol,
        timestamp=latest_row.name,
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
    create_tables()
    session = get_session()

    watchlist = fetch_sp500_tickers() if USE_SP500 else MANUAL_WATCHLIST
    print(f"Screening {len(watchlist)} ticker(s)...\n")

    all_data = fetch_multiple_symbols(watchlist, lookback_days=100)
    print(f"\nFetched data for {len(all_data)}/{len(watchlist)} tickers. Evaluating rules...\n")

    total_signals = 0
    all_triggered = []
    errors = 0

    for symbol, df in all_data.items():
        try:
            enriched = add_all_indicators(df)
            latest = enriched.iloc[-1]

            store_snapshot(session, symbol, latest)

            triggered = evaluate_rules(enriched, symbol)
            store_signals(session, triggered)
            all_triggered.extend(triggered)

            # With 500 tickers, only print the ones that actually matter —
            # a full per-ticker dump would be hundreds of lines of noise.
            if triggered:
                print(f"{symbol}: {len(triggered)} signal(s) triggered")
                for sig in triggered:
                    print(f"   [{sig['rule_name']}] {sig['details']}")

            total_signals += len(triggered)

        except Exception as e:
            errors += 1
            # Don't print every single error at scale — just count them.
            continue

    session.commit()
    session.close()

    # Send one batched Discord alert, including a heartbeat when no rules trigger.
    send_discord_alert(all_triggered, screened_count=len(all_data), error_count=errors)

    print(f"\nDone. Screened {len(all_data)} tickers, {total_signals} total signal(s) triggered, "
          f"{errors} ticker(s) failed to process.")


if __name__ == "__main__":
    run_screener()
