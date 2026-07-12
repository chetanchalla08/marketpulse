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

    if isinstance(bars.index, pd.MultiIndex):
        bars = bars.xs(symbol, level="symbol")

    df = bars[["open", "high", "low", "close", "volume"]].copy()
    df.index.name = "timestamp"
    return df


def fetch_multiple_symbols(symbols: list[str], lookback_days: int = 200) -> dict[str, pd.DataFrame]:
    """Fetch daily bars for a watchlist of symbols. Returns {symbol: DataFrame}."""
    result = {}
    for symbol in symbols:
        try:
            result[symbol] = fetch_daily_bars(symbol, lookback_days)
        except Exception as e:
            print(f"  [WARN] Failed to fetch {symbol}: {e}")
    return result


if __name__ == "__main__":
    df = fetch_daily_bars("AAPL", lookback_days=60)
    print(df.tail())
    print(f"\nFetched {len(df)} daily bars for AAPL.")
