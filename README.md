# MarketPulse Screener

A real-time equity screening engine that evaluates a watchlist of stocks against rule-based technical setups (RSI, MACD, VWAP), sends alerts when a setup triggers, and includes a backtesting module that validates each rule against 2 years of historical data.

## Why this exists

Most trading-related student projects try to *predict* stock prices with machine learning — an approach that's both a well-worn tutorial template and, from a finance standpoint, hard to defend (price prediction fights an efficient, close-to-random-walk market). MarketPulse takes a different, more honest approach: instead of predicting the future, it **detects when defined technical conditions occur** — the same kind of rule-based setups real discretionary and systematic traders actually use — and then backtests whether those setups have historically had any edge at all.

## Architecture

```
Alpaca Market Data API
        |
        v
  data_fetcher.py  ->  indicators.py (RSI, MACD, VWAP, computed from raw formulas)
        |
        v
   screener.py (rule engine)  --triggers-->  db.py (PostgreSQL / Supabase)
        |                                            |
        v                                            v
  alerts.py (Discord webhook)              backtest.py (historical validation)
        |
        v
  GitHub Actions (scheduled runs, weekdays market hours)
```

## Features

- **Indicator engine** — RSI, MACD, and VWAP implemented from their underlying mathematical formulas (not a black-box TA library), verified against synthetic test cases with known correct answers.
- **Rule-based screener** — three technical setups evaluated against a live watchlist: oversold-recovery (RSI + VWAP reclaim), MACD bullish crossover, and overbought warning.
- **Persistent storage** — every screening run stores indicator snapshots and triggered signals to a PostgreSQL database, building a real historical record over time.
- **Automated alerting** — triggered signals are pushed to Discord in real time via webhook.
- **Fully automated scheduling** — runs on GitHub Actions on a market-hours schedule, with no server or laptop required to stay on.
- **Backtesting engine** — replays all three rules against ~2 years of historical data with no lookahead bias, producing real win-rate and average-return statistics per rule.

## Backtest results

Backtested across AAPL, TSLA, NVDA, SPY, and MSFT over the trailing 2 years (153 total trigger events):

| Rule | Triggers | 1-day win rate | 3-day win rate | 5-day win rate | 3-day avg return |
|---|---|---|---|---|---|
| Oversold reclaim VWAP | 38 | 50.0% | **63.2%** | 55.3% | **+0.80%** |
| MACD bullish crossover | 99 | 53.5% | 51.5% | 51.5% | +0.48% |
| Overbought warning | 16 | 50.0% | 62.5% | 43.8% | +0.62% |

**Caveats, honestly stated:** this is a relatively small sample (5 tickers, ~150 events) over a period where markets broadly trended upward, and does not account for trading costs, slippage, or execution timing. These results should be read as "this rule shows a measurable historical edge worth further testing," not as a validated trading strategy.

## Tech stack

- **Python** — core application logic
- **PostgreSQL** (hosted on Supabase) — persistent storage for indicator history and signals
- **SQLAlchemy** — ORM / database layer
- **Alpaca Market Data API** — real-time and historical equity price data
- **GitHub Actions (YAML)** — CI/CD-style scheduled automation
- **Discord Webhooks** — real-time alerting

## Project structure

```
marketpulse/
├── src/
│   ├── indicators.py     # RSI, MACD, VWAP from raw formulas
│   ├── data_fetcher.py   # Alpaca API integration
│   ├── db.py              # database models + connection
│   ├── screener.py       # rule engine
│   ├── alerts.py          # Discord webhook alerting
│   └── backtest.py        # historical rule validation
├── tests/
│   └── test_indicators.py # indicator correctness tests
├── .github/workflows/
│   └── screener.yml       # scheduled cloud automation
├── run_screener.py        # main entry point — screen + alert + store
├── run_backtest.py        # backtest entry point
├── verify_week1.py        # data pipeline verification script
└── requirements.txt
```

## Running it locally

1. Clone the repo and set up a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and fill in:
   - Alpaca Paper Trading API key/secret ([alpaca.markets](https://alpaca.markets))
   - Supabase (or any PostgreSQL) connection string
   - A Discord webhook URL, if you want alerts

3. Create the database tables:
```bash
python -m src.db
```

4. Run the screener:
```bash
python run_screener.py
```

5. Run the backtest:
```bash
python run_backtest.py
```

## Automated runs

The screener runs automatically on GitHub Actions on weekdays during market hours (see `.github/workflows/screener.yml`), using repository secrets for credentials — no local machine needs to stay on.

## Adding a new rule

Rules are defined as small, independent functions in `src/screener.py` and registered in the `RULES` dictionary. A new rule automatically becomes available to both the live screener and the backtesting engine, since both read from the same registry — no logic duplication.

## Future improvements

- Expand the watchlist and backtest sample size for more statistically meaningful results
- Add transaction cost/slippage modeling to the backtest
- Build a lightweight dashboard for visualizing signal history
- Add position sizing / risk-based filtering on top of raw signal triggers
