import streamlit as st
import pandas as pd
from utils import (
    load_real_ohlc,
    disparity_index_optimized,
    auto_trade_executor,
    monthly_pnl_summary,
    daily_pnl_summary,
    reasoning_panel
)

st.set_page_config(page_title="Auto Paper Trading", layout="wide")
st.title("📈 Auto Paper Trading — NIFTY & BANKNIFTY")

paper_trading = st.toggle("🧪 Enable Paper Trading")

uploaded_file = st.file_uploader("Upload Live OHLC CSV (Date, Open, High, Low, Close)", type=["csv"])
if uploaded_file:
    df = load_real_ohlc(uploaded_file)

    results = {}
    for symbol, lot_size in [("NIFTY", 50), ("BANKNIFTY", 15)]:
        df_symbol = disparity_index_optimized(df.copy())
        paired_df = auto_trade_executor(df_symbol, symbol=symbol, lot_size=lot_size) if paper_trading else pd.DataFrame()
        results[symbol] = {"signals": df_symbol, "trades": paired_df}

    for symbol in ["NIFTY", "BANKNIFTY"]:
        st.header(f"📊 {symbol} Panel")
        st.subheader("📈 Signal Table")
        st.dataframe(results[symbol]["signals"].tail(20), use_container_width=True)

        st.subheader("📘 Trade Log")
        if not results[symbol]["trades"].empty:
            st.dataframe(results[symbol]["trades"], use_container_width=True)
            st.download_button(f"Download {symbol} Trade Log", results[symbol]["trades"].to_csv(index=False).encode("utf-8"), f"{symbol}_trade_log.csv", "text/csv")

            st.subheader("📆 Monthly PnL (Last 12 Months)")
            monthly_df = monthly_pnl_summary(results[symbol]["trades"])
            st.dataframe(monthly_df, use_container_width=True)
            st.download_button(f"Download {symbol} Monthly PnL", monthly_df.to_csv(index=False).encode("utf-8"), f"{symbol}_monthly_pnl.csv", "text/csv")
            st.line_chart(monthly_df.set_index("Month")["Net_PnL"])

            st.subheader("📅 Daily PnL (Last 30 Days)")
            daily_df = daily_pnl_summary(results[symbol]["trades"])
            st.dataframe(daily_df, use_container_width=True)
            st.download_button(f"Download {symbol} Daily PnL", daily_df.to_csv(index=False).encode("utf-8"), f"{symbol}_daily_pnl.csv", "text/csv")
        else:
            st.info(f"No trades executed for {symbol}. Toggle ON to activate paper trading.")

    st.subheader("🧠 Reasoning Panel (Latest Candle)")
    st.json(reasoning_panel(df))
