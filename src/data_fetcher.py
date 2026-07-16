"""
Pulls historical OHLCV bars from Alpaca and returns a pandas DataFrame
shaped for indicators.py (columns: open, high, low, close, volume; DatetimeIndex).

Setup:
1. Create a free account at https://alpaca.markets
2. Generate Paper Trading API keys (no funding needed, this is data-only use)
3. Copy .env.example to .env and fill in your keys
4. pip install -r requirements.txt
"""

import os
from datetime import datetime, timedelta

import pandas as pd
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")


def get_client() -> StockHistoricalDataClient:
    if not API_KEY or not SECRET_KEY:
        raise EnvironmentError(
            "ALPACA_API_KEY / ALPACA_SECRET_KEY not found. "
            "Copy .env.example to .env and fill in your keys."
        )
    return StockHistoricalDataClient(API_KEY, SECRET_KEY)


def fetch_daily_bars(symbol: str, lookback_days: int = 200) -> pd.DataFrame:
    """
    Fetch daily OHLCV bars for a single symbol, shaped for indicators.py.
    lookback_days=200 gives enough history for a 26-period MACD / 14-period RSI
    to have already "warmed up" by the most recent bar.
    """
    client = get_client()
    end = datetime.now()
    start = end - timedelta(days=lookback_days)

    request = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=TimeFrame.Day,
        start=start,
        end=end,
    )
    bars = client.get_stock_bars(request).df

    # Alpaca returns a multi-index (symbol, timestamp) when querying a single symbol too
    if isinstance(bars.index, pd.MultiIndex):
        bars = bars.xs(symbol, level="symbol")

    df = bars[["open", "high", "low", "close", "volume"]].copy()
    df.index.name = "timestamp"
    return df


def fetch_multiple_symbols(symbols: list[str], lookback_days: int = 200, batch_size: int = 100) -> dict[str, pd.DataFrame]:
    """
    Fetch daily bars for many symbols efficiently.

    Naively calling fetch_daily_bars() in a loop means one HTTP request per
    symbol -- for 500 S&P 500 tickers, that's 500 round trips, which is slow
    and risks hitting Alpaca's rate limits. Instead, Alpaca's API accepts a
    LIST of symbols in a single request and returns all their bars together,
    so we batch symbols into chunks (default 100 per request) and issue far
    fewer, larger requests instead.

    Returns {symbol: DataFrame}, same shape as calling fetch_daily_bars()
    individually -- so this is a drop-in replacement anywhere you're
    screening/backtesting a list of tickers.
    """
    client = get_client()
    end = datetime.now()
    start = end - timedelta(days=lookback_days)

    result: dict[str, pd.DataFrame] = {}

    for i in range(0, len(symbols), batch_size):
        batch = symbols[i : i + batch_size]
        print(f"  Fetching batch {i // batch_size + 1} ({len(batch)} symbols)...")

        try:
            request = StockBarsRequest(
                symbol_or_symbols=batch,
                timeframe=TimeFrame.Day,
                start=start,
                end=end,
            )
            bars = client.get_stock_bars(request).df

            if bars.empty:
                continue

            for symbol in batch:
                if symbol in bars.index.get_level_values("symbol"):
                    symbol_df = bars.xs(symbol, level="symbol")[["open", "high", "low", "close", "volume"]].copy()
                    symbol_df.index.name = "timestamp"
                    result[symbol] = symbol_df

        except Exception as e:
            # A single bad/invalid symbol in a batch fails the WHOLE batch request --
            # rather than losing all ~100 good symbols over one bad one, retry each
            # symbol in this batch individually and just skip the ones that fail.
            print(f"  [WARN] Batch starting at index {i} failed ({e}) -- retrying individually...")
            for symbol in batch:
                try:
                    result[symbol] = fetch_daily_bars(symbol, lookback_days)
                except Exception:
                    print(f"    [WARN] Skipping invalid/unavailable symbol: {symbol}")

    return result


if __name__ == "__main__":
    # Quick manual test: fetch AAPL and print the last 5 rows
    df = fetch_daily_bars("AAPL", lookback_days=60)
    print(df.tail())
    print(f"\nFetched {len(df)} daily bars for AAPL.")
