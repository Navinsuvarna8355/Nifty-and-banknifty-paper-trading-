import streamlit as st
import pandas as pd
from utils import (
    load_real_ohlc,
    disparity_index_optimized,
    auto_trade_executor,
    monthly_pnl_summary,
    reasoning_panel
)

st.set_page_config(page_title="📊 Paper Trading Dashboard", layout="wide")
st.title("📈 Auto Paper Trading — Disparity Index Strategy")

symbol = st.selectbox("Select Symbol", ["BANKNIFTY", "NIFTY"])
lot_size = 15 if symbol == "BANKNIFTY" else 50
paper_trading = st.toggle("🧪 Enable Paper Trading")

uploaded_file = st.file_uploader("Upload Live OHLC CSV", type=["csv"])
if uploaded_file:
    df = load_real_ohlc(uploaded_file)
    df = disparity_index_optimized(df)
    
    if paper_trading:
        paired_df = auto_trade_executor(df, symbol=symbol, lot_size=lot_size)
        st.success("✅ Trades executed based on strategy")
    else:
        paired_df = pd.DataFrame()

    st.subheader("📈 Signal Table")
    st.dataframe(df.tail(20), use_container_width=True)

    st.subheader("📘 Trade Log")
    if not paired_df.empty:
        st.dataframe(paired_df, use_container_width=True)
        st.download_button("Download Trade Log", paired_df.to_csv(index=False).encode("utf-8"), "trade_log.csv", "text/csv")
    else:
        st.info("Paper trading is OFF. No trades executed.")

    st.subheader("🧠 Reasoning Panel")
    st.json(reasoning_panel(df))

    st.subheader("📆 Monthly PnL Summary")
    if not paired_df.empty:
        monthly_df = monthly_pnl_summary(paired_df)
        st.dataframe(monthly_df, use_container_width=True)
        st.download_button("Download Monthly PnL", monthly_df.to_csv(index=False).encode("utf-8"), "monthly_pnl.csv", "text/csv")
        st.line_chart(monthly_df.set_index("Month")["Net_PnL"])

