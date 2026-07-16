"""
Fetches the current list of S&P 500 ticker symbols from Wikipedia's
maintained table, and caches it locally so we're not re-scraping on
every single run.
"""

import os
import io
import urllib.request
import pandas as pd

CACHE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sp500_tickers.csv")
WIKI_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"


def normalize_for_alpaca(symbol: str) -> str:
    """Alpaca expects class-share tickers like BRK.B, not BRK-B."""
    return symbol.replace("-", ".")


def fetch_sp500_tickers(force_refresh: bool = False) -> list[str]:
    """
    Returns the list of S&P 500 ticker symbols. Uses a local cache
    (data/sp500_tickers.csv) unless force_refresh=True or no cache exists yet.
    """
    if not force_refresh and os.path.exists(CACHE_PATH):
        cached = pd.read_csv(CACHE_PATH)
        return [normalize_for_alpaca(symbol) for symbol in cached["symbol"].tolist()]

    # Wikipedia rejects requests without a browser-like User-Agent header
    # (returns HTTP 403), so we fetch the page manually first instead of
    # letting pandas make the raw request itself.
    request = urllib.request.Request(
        WIKI_URL,
        headers={"User-Agent": "Mozilla/5.0 (compatible; MarketPulse/1.0)"},
    )
    with urllib.request.urlopen(request) as response:
        html = response.read().decode("utf-8")

    tables = pd.read_html(io.StringIO(html))
    sp500_table = tables[0]  # the first table on the page is the current constituent list
    tickers = sp500_table["Symbol"].tolist()

    tickers = [normalize_for_alpaca(t) for t in tickers]

    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    pd.DataFrame({"symbol": tickers}).to_csv(CACHE_PATH, index=False)

    return tickers


if __name__ == "__main__":
    tickers = fetch_sp500_tickers(force_refresh=True)
    print(f"Fetched {len(tickers)} S&P 500 tickers, cached to {CACHE_PATH}")
    print(tickers[:10], "...")
