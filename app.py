import streamlit as st
from utils import monthly_pnl_summary, daily_pnl_summary

st.title("📈 Auto Paper Trading — NIFTY & BANKNIFTY")
st.subheader("📊 PnL Summary Dashboard")

symbol = st.selectbox("Choose Symbol", options=["NIFTY", "BANKNIFTY"])

try:
    trades_df = results[symbol]["trades"]

    st.markdown("### 📆 Monthly PnL Summary")
    monthly_df = monthly_pnl_summary(trades_df)
    st.dataframe(monthly_df)

    st.markdown("### 📅 Daily PnL Summary")
    daily_df = daily_pnl_summary(trades_df)
    st.dataframe(daily_df)

except KeyError as e:
    st.error(f"⚠️ Data error: {e}")
except Exception as e:
    st.error("🚨 Unexpected error occurred.")
    st.stop()
