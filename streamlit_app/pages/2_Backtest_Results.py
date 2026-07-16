import sys
from pathlib import Path


def _repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "src" / "db.py").exists():
            return parent
    raise RuntimeError("Could not locate repo root (src/db.py not found)")


sys.path.insert(0, str(_repo_root()))

import pandas as pd
import plotly.express as px
import streamlit as st

from src.db import get_session, BacktestResult

st.set_page_config(page_title="Backtest Results | MarketPulse", page_icon="📈", layout="wide")
st.title("Backtest Results")

session = get_session()
try:
    run_ats = [
        r[0] for r in session.query(BacktestResult.run_at).distinct().order_by(BacktestResult.run_at.desc()).all()
    ]
finally:
    session.close()

if not run_ats:
    st.info("No backtest runs recorded yet. Run `python run_backtest.py` first.")
    st.stop()

selected_run = st.selectbox("Backtest run", run_ats, format_func=lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S"))

session = get_session()
try:
    results = (
        session.query(BacktestResult)
        .filter(BacktestResult.run_at == selected_run)
        .order_by(BacktestResult.rule_name, BacktestResult.horizon_days)
        .all()
    )
finally:
    session.close()

df = pd.DataFrame(
    [
        {
            "rule": r.rule_name,
            "horizon_days": r.horizon_days,
            "trigger_count": r.trigger_count,
            "win_rate_pct": r.win_rate_pct,
            "avg_return_pct": r.avg_return_pct,
        }
        for r in results
    ]
)
df["horizon"] = df["horizon_days"].astype(str) + "d"

col1, col2 = st.columns(2)
with col1:
    fig_win = px.bar(
        df, x="horizon", y="win_rate_pct", color="rule", barmode="group",
        title="Win rate by rule and horizon", labels={"win_rate_pct": "Win rate %"},
    )
    st.plotly_chart(fig_win, use_container_width=True)
with col2:
    fig_ret = px.bar(
        df, x="horizon", y="avg_return_pct", color="rule", barmode="group",
        title="Avg return by rule and horizon", labels={"avg_return_pct": "Avg return %"},
    )
    st.plotly_chart(fig_ret, use_container_width=True)

st.dataframe(
    df[["rule", "horizon", "trigger_count", "win_rate_pct", "avg_return_pct"]],
    use_container_width=True,
    hide_index=True,
)
