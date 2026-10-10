"""
Financial Market Data Analyzer
Run locally: streamlit run app.py
Uses sample historical prices by default; optionally upload your own CSV.
Educational analysis only — not investment advice.
"""
from pathlib import Path
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Financial Market Data Analyzer", page_icon="📈", layout="wide")

st.title("📈 Financial Market Data Analyzer")
st.caption("Explore historical price movements, returns, volatility and correlations. Educational use only — not investment advice.")

DATA_PATH = Path(__file__).parent / "data" / "sample_prices.csv"

@st.cache_data
def load_sample():
    return pd.read_csv(DATA_PATH, parse_dates=["Date"])

def prepare_data(raw):
    raw = raw.copy()
    raw.columns = [str(c).strip() for c in raw.columns]
    if "Date" not in raw.columns:
        raise ValueError("CSV must contain a Date column.")
    raw["Date"] = pd.to_datetime(raw["Date"], errors="coerce")
    raw = raw.dropna(subset=["Date"])
    value_cols = [c for c in raw.columns if c != "Date"]
    if not value_cols:
        raise ValueError("CSV must contain at least one instrument price column.")
    for c in value_cols:
        raw[c] = pd.to_numeric(raw[c], errors="coerce")
    raw = raw.sort_values("Date").drop_duplicates(subset=["Date"]).set_index("Date")
    raw = raw[value_cols].ffill().dropna(how="all")
    if raw.empty:
        raise ValueError("No usable numeric price data found.")
    return raw

with st.sidebar:
    st.header("Data")
    uploaded = st.file_uploader("Upload price CSV (Date + one column per instrument)", type=["csv"])
    st.info("CSV format: Date, Instrument A, Instrument B, ...")
    st.caption("The included dataset is synthetic sample data, not real market quotes.")

try:
    raw = prepare_data(pd.read_csv(uploaded, parse_dates=["Date"]) if uploaded else load_sample())
except Exception as e:
    st.error(f"Could not load data: {e}")
    st.stop()

instruments = list(raw.columns)
with st.sidebar:
    selected = st.multiselect("Instruments to compare", instruments, default=instruments[:min(4, len(instruments))])
    start_date = st.date_input("Start date", value=raw.index.min().date(), min_value=raw.index.min().date(), max_value=raw.index.max().date())
    end_date = st.date_input("End date", value=raw.index.max().date(), min_value=raw.index.min().date(), max_value=raw.index.max().date())

if not selected:
    st.warning("Select at least one instrument in the sidebar.")
    st.stop()
if start_date > end_date:
    st.error("Start date must be on or before end date.")
    st.stop()

prices = raw.loc[(raw.index.date >= start_date) & (raw.index.date <= end_date), selected].dropna(how="all")
if len(prices) < 2:
    st.warning("Choose a date range containing at least two observations.")
    st.stop()

returns = prices.pct_change().dropna(how="all")
total_returns = (prices.iloc[-1] / prices.iloc[0] - 1) * 100
daily_vol = returns.std() * np.sqrt(252) * 100
best = total_returns.idxmax()
worst = total_returns.idxmin()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Instruments", len(selected))
c2.metric("Observations", len(prices))
c3.metric("Best total return", best, f"{total_returns[best]:.2f}%")
c4.metric("Highest annualized volatility", daily_vol.idxmax(), f"{daily_vol.max():.2f}%")

tab1, tab2, tab3, tab4 = st.tabs(["Price trends", "Returns", "Risk & performance", "Correlation"])

with tab1:
    st.subheader("Normalized price performance")
    normalized = prices / prices.iloc[0] * 100
    fig, ax = plt.subplots(figsize=(11, 4.5))
    normalized.plot(ax=ax, linewidth=1.8)
    ax.set_ylabel("Index (first observation = 100)")
    ax.set_xlabel("Date")
    ax.grid(True, alpha=0.25)
    st.pyplot(fig)
    plt.close(fig)
    st.caption("Normalization lets you compare percentage performance even when instruments start at different prices.")

with tab2:
    st.subheader("Daily percentage returns")
    fig, ax = plt.subplots(figsize=(11, 4.5))
    (returns * 100).plot(ax=ax, alpha=0.85)
    ax.set_ylabel("Daily return (%)")
    ax.set_xlabel("Date")
    ax.grid(True, alpha=0.25)
    st.pyplot(fig)
    plt.close(fig)
    st.dataframe((returns * 100).describe().T.rename(columns={"mean":"Mean (%)","std":"Std. dev. (%)","min":"Min (%)","max":"Max (%)"}).round(3), use_container_width=True)

with tab3:
    st.subheader("Performance and risk summary")
    summary = pd.DataFrame({
        "Start Price": prices.iloc[0],
        "End Price": prices.iloc[-1],
        "Total Return (%)": total_returns,
        "Mean Daily Return (%)": returns.mean() * 100,
        "Annualized Volatility (%)": daily_vol,
        "Observations": prices.count()
    }).sort_values("Total Return (%)", ascending=False)
    st.dataframe(summary.round(3), use_container_width=True)
    fig, ax = plt.subplots(figsize=(9, 4))
    summary["Total Return (%)"].sort_values().plot(kind="bar", ax=ax)
    ax.set_ylabel("Total return (%)")
    ax.set_xlabel("Instrument")
    ax.grid(axis="y", alpha=0.25)
    st.pyplot(fig)
    plt.close(fig)
    st.caption("Annualized volatility is the standard deviation of daily returns multiplied by √252, a common trading-day approximation.")

with tab4:
    st.subheader("Daily return correlation")
    corr = returns.corr()
    fig, ax = plt.subplots(figsize=(7, 5))
    image = ax.imshow(corr, vmin=-1, vmax=1, aspect="auto")
    ax.set_xticks(range(len(corr.columns)), corr.columns, rotation=35, ha="right")
    ax.set_yticks(range(len(corr.index)), corr.index)
    for i in range(len(corr.index)):
        for j in range(len(corr.columns)):
            if pd.notna(corr.iloc[i, j]):
                ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=9)
    fig.colorbar(image, ax=ax, label="Correlation")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    st.caption("Correlation describes how daily returns moved together in this selected period; it does not imply causation.")

st.subheader("Data preview")
st.dataframe(prices.tail(15).round(2), use_container_width=True)
csv = prices.reset_index().to_csv(index=False).encode("utf-8")
st.download_button("Download selected price data as CSV", data=csv, file_name="selected_market_prices.csv", mime="text/csv")

st.divider()
st.markdown("**Method notes**")
st.markdown("""
- Total return is calculated from the first and last available prices in the selected date range.
- Daily return is the percentage change between consecutive observations.
- Volatility is annualized using 252 trading days.
- Sample data are synthetic and only demonstrate the dashboard. Upload a real historical-price CSV before drawing conclusions about actual markets.
""")
