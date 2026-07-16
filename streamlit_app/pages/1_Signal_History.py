import sys
from datetime import date, timedelta
from pathlib import Path


def _repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "src" / "db.py").exists():
            return parent
    raise RuntimeError("Could not locate repo root (src/db.py not found)")


sys.path.insert(0, str(_repo_root()))

import pandas as pd
import streamlit as st

from src.db import get_session, Signal

st.set_page_config(page_title="Signal History | MarketPulse", page_icon="📈", layout="wide")
st.title("Signal History")

session = get_session()
try:
    rule_names = [r[0] for r in session.query(Signal.rule_name).distinct().all()]
finally:
    session.close()

col1, col2, col3 = st.columns([2, 2, 3])
symbol = col1.text_input("Symbol (optional)", "").strip().upper()
rule_name = col2.selectbox("Rule", ["All"] + sorted(rule_names))
date_range = col3.date_input(
    "Date range",
    value=(date.today() - timedelta(days=30), date.today()),
)

session = get_session()
try:
    query = session.query(Signal)
    if symbol:
        query = query.filter(Signal.symbol == symbol)
    if rule_name != "All":
        query = query.filter(Signal.rule_name == rule_name)
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = date_range
        query = query.filter(Signal.timestamp >= start, Signal.timestamp < end + timedelta(days=1))
    signals = query.order_by(Signal.timestamp.desc()).limit(1000).all()
finally:
    session.close()

st.caption(f"{len(signals)} signal(s) matching filters (showing up to 1000, most recent first).")

if signals:
    df = pd.DataFrame(
        [
            {
                "timestamp": s.timestamp,
                "symbol": s.symbol,
                "rule": s.rule_name,
                "close": s.close_at_signal,
                "details": s.details,
            }
            for s in signals
        ]
    )
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No signals match these filters.")
