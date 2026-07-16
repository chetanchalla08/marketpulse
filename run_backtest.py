"""
Runs the backtest across the full S&P 500 over ~2 years of history and
prints a summary report -- the real, quotable numbers for your resume/README.

Note: at 500-ticker x 2-year scale, this takes noticeably longer than the
5-stock version did (still batched, but there's simply more data to process).
Consider running this as a one-off rather than something you rerun casually.

Run with: python run_backtest.py
"""

from src.data_fetcher import fetch_multiple_symbols
from src.indicators import add_all_indicators
from src.backtest import backtest_symbol, summarize_results
from src.sp500 import fetch_sp500_tickers

USE_SP500 = True
MANUAL_WATCHLIST = ["AAPL", "TSLA", "NVDA", "SPY", "MSFT"]
LOOKBACK_DAYS = 730  # ~2 years


def run_backtest():
    watchlist = fetch_sp500_tickers() if USE_SP500 else MANUAL_WATCHLIST
    print(f"Backtesting {len(watchlist)} ticker(s) over the last {LOOKBACK_DAYS} days...\n")

    all_data = fetch_multiple_symbols(watchlist, lookback_days=LOOKBACK_DAYS)
    print(f"\nFetched data for {len(all_data)}/{len(watchlist)} tickers. Running backtest...\n")

    all_results = []
    for symbol, df in all_data.items():
        try:
            enriched = add_all_indicators(df)
            results = backtest_symbol(enriched, symbol)
            all_results.extend(results)
        except Exception:
            continue

    print(f"Total trigger events across watchlist: {len(all_results)}\n")

    if not all_results:
        print("No historical triggers found.")
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
