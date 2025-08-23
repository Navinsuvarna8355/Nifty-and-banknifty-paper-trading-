import streamlit as st
import datetime
import pytz
from utils import (
    fetch_live_ohlc,
    disparity_index_optimized,
    auto_trade_executor,
    monthly_pnl_summary,
    daily_pnl_summary,
    reasoning_panel
)

# Timezone setup
IST = pytz.timezone("Asia/Kolkata")
now = datetime.datetime.now(IST)
market_open = datetime.time(9, 15)
market_close = datetime.time(15, 30)
is_weekday = now.weekday() < 5
is_market_hours = market_open <= now.time() <= market_close

# UI
st.set_page_config(page_title="Live Paper Trading", layout="wide")
st.title("📈 Auto Paper Trading — NIFTY & BANKNIFTY")
st.caption(f"🕒 {now.strftime('%A %H:%M:%S')} IST")

paper_trading = st.toggle("🧪 Enable Paper Trading")

if is_weekday and is_market_hours and paper_trading:
    st.success("✅ Paper trading active: Market is open and toggle is ON.")

    results = {}
    for symbol in ["NIFTY", "BANKNIFTY"]:
        df = fetch_live_ohlc(symbol)
        df = disparity_index_optimized(df)
        paired_df = auto_trade_executor(df, symbol=symbol)
        results[symbol] = {"signals": df, "trades": paired_df}

    for symbol in ["NIFTY", "BANKNIFTY"]:
        st.header(f"📊 {symbol} Panel")
        st.subheader("📈 Signal Table")
        st.dataframe(results[symbol]["signals"].tail(20), use_container_width=True)

        st.subheader("📘 Trade Log")
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

    st.subheader("🧠 Reasoning Panel")
    st.json(reasoning_panel(results["NIFTY"]["signals"]))  # Show NIFTY's latest signal
else:
    st.warning("⛔ Trades paused: Either market is closed or toggle is OFF.")
