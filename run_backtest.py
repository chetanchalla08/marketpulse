"""
Week 4 milestone script: runs the backtest across your watchlist over
~2 years of history and prints a summary report -- the real, quotable
numbers for your resume/README.

Run with: python run_backtest.py
"""

from src.data_fetcher import fetch_daily_bars
from src.indicators import add_all_indicators
from src.backtest import backtest_symbol, summarize_results

WATCHLIST = ["AAPL", "TSLA", "NVDA", "SPY", "MSFT"]
LOOKBACK_DAYS = 730  # ~2 years


def run_backtest():
    all_results = []

    print(f"Backtesting {WATCHLIST} over the last {LOOKBACK_DAYS} days...\n")

    for symbol in WATCHLIST:
        try:
            df = fetch_daily_bars(symbol, lookback_days=LOOKBACK_DAYS)
            enriched = add_all_indicators(df)
            results = backtest_symbol(enriched, symbol)
            all_results.extend(results)
            print(f"  {symbol}: {len(results)} historical trigger(s) found across all rules")
        except Exception as e:
            print(f"  [ERROR] {symbol}: {e}")

    print(f"\nTotal trigger events across watchlist: {len(all_results)}\n")

    if not all_results:
        print("No historical triggers found -- try widening the watchlist or lookback period.")
        return

    summary = summarize_results(all_results)

    print("=" * 90)
    print("BACKTEST SUMMARY (all symbols combined, per rule)")
    print("=" * 90)
    for _, row in summary.iterrows():
        print(f"\nRule: {row['rule_name']}")
        print(f"  Triggered {int(row['trigger_count'])} times")
        print(f"  1-day:  win rate {row['win_rate_1d']:.1f}%  |  avg return {row['avg_return_1d_pct']:+.2f}%")
        print(f"  3-day:  win rate {row['win_rate_3d']:.1f}%  |  avg return {row['avg_return_3d_pct']:+.2f}%")
        print(f"  5-day:  win rate {row['win_rate_5d']:.1f}%  |  avg return {row['avg_return_5d_pct']:+.2f}%")

    print("\n" + "=" * 90)
    print("Save these numbers -- this is your real, quotable backtest result for your resume/README.")


if __name__ == "__main__":
    run_backtest()
