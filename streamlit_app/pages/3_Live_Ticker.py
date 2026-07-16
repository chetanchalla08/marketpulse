import sys
from pathlib import Path


def _repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "src" / "db.py").exists():
            return parent
    raise RuntimeError("Could not locate repo root (src/db.py not found)")


sys.path.insert(0, str(_repo_root()))

import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from src.data_fetcher import fetch_daily_bars
from src.indicators import add_all_indicators

st.set_page_config(page_title="Live Ticker | MarketPulse", page_icon="📈", layout="wide")
st.title("Live Ticker")
st.caption("Fetches live from Alpaca and computes indicators on the spot — not read from the database.")

symbol = st.text_input("Symbol", "AAPL").strip().upper()
lookback_days = st.slider("Lookback (days)", min_value=30, max_value=730, value=200, step=10)

if st.button("Fetch", type="primary") or "last_symbol" not in st.session_state:
    st.session_state["last_symbol"] = symbol

if symbol:
    with st.spinner(f"Fetching {symbol} from Alpaca..."):
        try:
            bars = fetch_daily_bars(symbol, lookback_days=lookback_days)
            enriched = add_all_indicators(bars)
        except Exception as e:
            st.error(f"Failed to fetch/compute indicators for {symbol}: {e}")
            st.stop()

    latest = enriched.iloc[-1]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Close", f"${latest['close']:.2f}")
    col2.metric("RSI", f"{latest['rsi']:.1f}")
    col3.metric("MACD hist", f"{latest['macd_hist']:.3f}")
    col4.metric("VWAP", f"${latest['vwap']:.2f}")

    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True, row_heights=[0.5, 0.25, 0.25],
        vertical_spacing=0.05, subplot_titles=("Price vs VWAP", "RSI", "MACD"),
    )
    fig.add_trace(go.Scatter(x=enriched.index, y=enriched["close"], name="Close"), row=1, col=1)
    fig.add_trace(go.Scatter(x=enriched.index, y=enriched["vwap"], name="VWAP"), row=1, col=1)

    fig.add_trace(go.Scatter(x=enriched.index, y=enriched["rsi"], name="RSI"), row=2, col=1)
    fig.add_hline(y=70, line_dash="dot", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color="green", row=2, col=1)

    fig.add_trace(go.Scatter(x=enriched.index, y=enriched["macd"], name="MACD"), row=3, col=1)
    fig.add_trace(go.Scatter(x=enriched.index, y=enriched["macd_signal"], name="Signal"), row=3, col=1)
    fig.add_trace(go.Bar(x=enriched.index, y=enriched["macd_hist"], name="Histogram"), row=3, col=1)

    fig.update_layout(height=800, legend=dict(orientation="h"))
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(enriched.tail(20).sort_index(ascending=False), use_container_width=True)
