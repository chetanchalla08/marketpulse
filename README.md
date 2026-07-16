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

The Python pipeline above is the sole writer to Postgres. Two read paths sit on top of it:

```
                                    +-------------------+
                                    |   PostgreSQL /     |
                                    |     Supabase        |
                                    +----------+----------+
                                     ^         |
                       (writes only)|         | (reads only)
                                     |         v
   run_screener.py / run_backtest.py    api/ (Spring Boot REST API)
                                                    |
                                                    v
                                          frontend/ (React dashboard)

   streamlit_app/ (internal tool) -------> reads Postgres + Alpaca directly,
                                            independent of api/ and frontend/
```

## Features

- **Indicator engine** — RSI, MACD, and VWAP implemented from their underlying mathematical formulas (not a black-box TA library), verified against synthetic test cases with known correct answers.
- **Rule-based screener** — three technical setups evaluated against a live watchlist: oversold-recovery (RSI + VWAP reclaim), MACD bullish crossover, and overbought warning.
- **Persistent storage** — every screening run stores indicator snapshots and triggered signals to a PostgreSQL database, building a real historical record over time.
- **Automated alerting** — triggered signals are pushed to Discord in real time via webhook.
- **Fully automated scheduling** — runs on GitHub Actions on a market-hours schedule, with no server or laptop required to stay on.
- **Backtesting engine** — replays all three rules against ~2 years of historical data with no lookahead bias, producing real win-rate and average-return statistics per rule, persisted to the database for every run.
- **REST API** — a read-only Spring Boot service exposes signals, the latest indicator snapshot per symbol, and backtest results to any client, backed by the same Postgres database.
- **React dashboard** — a live view of signals, the full S&P 500 screener table, and backtest results with charts, talking to the Spring Boot API.
- **Streamlit internal tool** — a separate, lightweight app for ad-hoc exploration: signal history, backtest run comparisons, and live single-ticker charting, built directly on the `src/` modules.

## Backtest results

Backtested across AAPL, TSLA, NVDA, SPY, and MSFT over the trailing 2 years (153 total trigger events):

| Rule | Triggers | 1-day win rate | 3-day win rate | 5-day win rate | 3-day avg return |
|---|---|---|---|---|---|
| Oversold reclaim VWAP | 38 | 50.0% | **63.2%** | 55.3% | **+0.80%** |
| MACD bullish crossover | 99 | 53.5% | 51.5% | 51.5% | +0.48% |
| Overbought warning | 16 | 50.0% | 62.5% | 43.8% | +0.62% |

**Caveats, honestly stated:** this is a relatively small sample (5 tickers, ~150 events) over a period where markets broadly trended upward, and does not account for trading costs, slippage, or execution timing. These results should be read as "this rule shows a measurable historical edge worth further testing," not as a validated trading strategy.

## Tech stack

- **Python** — core screening/backtesting application logic
- **PostgreSQL** (hosted on Supabase) — persistent storage for indicator history, signals, and backtest results
- **SQLAlchemy** — ORM / database layer
- **Alpaca Market Data API** — real-time and historical equity price data
- **GitHub Actions (YAML)** — CI/CD-style scheduled automation
- **Discord Webhooks** — real-time alerting
- **Java / Spring Boot / Spring Data JPA** — read-only REST API in front of Postgres (`api/`)
- **React / TypeScript / Vite** — dashboard UI (`frontend/`), using TanStack Query for data fetching and Recharts for charts
- **Streamlit / Plotly** — internal exploration tool (`streamlit_app/`), built directly on the Python `src/` modules

## Project structure

```
marketpulse/
├── src/
│   ├── indicators.py     # RSI, MACD, VWAP from raw formulas
│   ├── data_fetcher.py   # Alpaca API integration
│   ├── db.py              # database models + connection (IndicatorSnapshot, Signal, BacktestResult)
│   ├── screener.py       # rule engine
│   ├── alerts.py          # Discord webhook alerting
│   └── backtest.py        # historical rule validation
├── tests/
│   └── test_indicators.py # indicator correctness tests
├── .github/workflows/
│   └── screener.yml       # scheduled cloud automation
├── run_screener.py        # main entry point — screen + alert + store
├── run_backtest.py        # backtest entry point — also persists results to backtest_results
├── verify_week1.py        # data pipeline verification script
├── requirements.txt
├── api/                    # Spring Boot read-only REST API (Java/Maven)
│   ├── pom.xml
│   └── src/main/java/com/marketpulse/api/
│       ├── entity/         # JPA entities mapped to the existing Postgres tables
│       ├── repository/     # Spring Data repositories (incl. latest-per-symbol query)
│       ├── dto/             # flat response records
│       ├── controller/     # /api/signals, /api/indicators, /api/backtest, /api/symbols
│       └── config/         # CORS config
├── frontend/                # React + TypeScript dashboard (Vite)
│   └── src/
│       ├── api/              # typed fetch client for the Spring Boot API
│       └── pages/            # Signals, Screener, Backtest views
└── streamlit_app/           # internal exploration tool (imports src/ directly)
    ├── app.py                # landing page with summary metrics
    └── pages/                # Signal History, Backtest Results, Live Ticker
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

5. Run the backtest (also persists results to `backtest_results` for the API/dashboard/Streamlit to read):
```bash
python run_backtest.py
```

### Spring Boot API (`api/`)

Requires Java 17+ and Maven. The API connects read-only to the same Postgres database, but needs its datasource configured separately from Python's `DATABASE_URL` since Spring's JDBC driver expects `jdbc:postgresql://...` plus a separate username/password rather than one connection-string env var:

```bash
export SPRING_DATASOURCE_URL=jdbc:postgresql://<host>:<port>/<db>   # same host/port/db as DATABASE_URL
export SPRING_DATASOURCE_USERNAME=<user>
export SPRING_DATASOURCE_PASSWORD=<password>
cd api && mvn spring-boot:run
```

`api/run-local.sh` does this automatically by parsing the repo's `.env` — run `./api/run-local.sh` from `api/` instead of setting the env vars by hand. The API listens on `http://localhost:8080`.

### React dashboard (`frontend/`)

Requires Node.js. Proxies `/api/*` to the Spring Boot API at `localhost:8080` in dev (see `vite.config.ts`), so start the API first.

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

### Streamlit internal tool (`streamlit_app/`)

Independent of the API/React — reads Postgres and Alpaca directly via `src/`. Install its extra dependencies, then run from the repo root:

```bash
pip install -r streamlit_app/requirements.txt
streamlit run streamlit_app/app.py
```

## Automated runs

The screener runs automatically on GitHub Actions on weekdays during market hours (see `.github/workflows/screener.yml`), using repository secrets for credentials — no local machine needs to stay on.

## Adding a new rule

Rules are defined as small, independent functions in `src/screener.py` and registered in the `RULES` dictionary. A new rule automatically becomes available to both the live screener and the backtesting engine, since both read from the same registry — no logic duplication.

## Future improvements

- Expand the backtest sample size (now across the full S&P 500) for even more statistically meaningful results
- Add transaction cost/slippage modeling to the backtest
- Add position sizing / risk-based filtering on top of raw signal triggers
- Deploy the API, dashboard, and Streamlit tool (currently local-only) — e.g. Spring Boot to Render/Fly.io, React to Vercel/Netlify, Streamlit to Streamlit Community Cloud
