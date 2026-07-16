"""
MarketPulse internal dashboard: ad-hoc exploration of the screener's data,
built directly on top of src/ (no API layer) for fast iteration.

Run with: streamlit run streamlit_app/app.py
"""

import sys
from pathlib import Path


def _repo_root() -> Path:
    # Streamlit runs each page as a standalone script and only puts that
    # script's own directory on sys.path, so every entry file has to locate
    # the repo root itself before `from src...` imports will resolve.
    for parent in Path(__file__).resolve().parents:
        if (parent / "src" / "db.py").exists():
            return parent
    raise RuntimeError("Could not locate repo root (src/db.py not found)")


sys.path.insert(0, str(_repo_root()))

import streamlit as st
from sqlalchemy import func

from src.db import get_session, IndicatorSnapshot, Signal, BacktestResult

st.set_page_config(page_title="MarketPulse", page_icon="📈", layout="wide")

st.title("MarketPulse")
st.caption("Internal dashboard for exploring the S&P 500 screener's signal and backtest history.")

session = get_session()
try:
    symbol_count = session.query(func.count(func.distinct(IndicatorSnapshot.symbol))).scalar() or 0
    signal_count = session.query(func.count(Signal.id)).scalar() or 0
    last_run = session.query(func.max(IndicatorSnapshot.timestamp)).scalar()
    backtest_runs = session.query(func.count(func.distinct(BacktestResult.run_at))).scalar() or 0
finally:
    session.close()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Tickers screened", symbol_count)
col2.metric("Signals triggered (all time)", signal_count)
col3.metric("Backtest runs recorded", backtest_runs)
col4.metric("Last screener run", last_run.strftime("%Y-%m-%d %H:%M") if last_run else "—")

st.markdown(
    """
    Use the pages in the sidebar to dig in:

    - **Signal History** — every rule trigger, filterable by symbol, rule, and date range
    - **Backtest Results** — win rate / average return per rule, per run
    - **Live Ticker** — pull a symbol live from Alpaca and chart its indicators right now
    """
)
