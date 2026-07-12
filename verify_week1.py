"""
Week 1 milestone check: fetch real data for a small watchlist, compute all
three indicators, and print the latest values so you can eyeball them
against TradingView/Yahoo Finance and confirm the math is trustworthy.

Run with: python verify_week1.py
"""

from src.data_fetcher import fetch_daily_bars
from src.indicators import add_all_indicators

WATCHLIST = ["AAPL", "TSLA", "NVDA", "SPY", "MSFT"]

if __name__ == "__main__":
    print(f"Fetching data and computing indicators for {WATCHLIST}...\n")

    for symbol in WATCHLIST:
        try:
            df = fetch_daily_bars(symbol, lookback_days=100)
            enriched = add_all_indicators(df)
            latest = enriched.iloc[-1]

            print(f"{symbol}:")
            print(f"  Close:  {latest['close']:.2f}")
            print(f"  RSI:    {latest['rsi']:.2f}")
            print(f"  MACD:   {latest['macd']:.4f}  (signal: {latest['macd_signal']:.4f}, hist: {latest['macd_hist']:.4f})")
            print(f"  VWAP:   {latest['vwap']:.2f}")
            print()
        except Exception as e:
            print(f"  [ERROR] {symbol}: {e}\n")

    print("Cross-check a couple of these RSI/MACD values against TradingView for the same symbol/date.")
    print("If they're within a small rounding tolerance, Week 1 is verified — move on to Week 2 (screening + database).")
