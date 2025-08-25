import pandas as pd
import streamlit as st

def monthly_pnl_summary(df):
    if df.empty or "Exit Time" not in df.columns:
        return pd.DataFrame(columns=["Month", "Total_Trades", "Total_Profit", "Total_Loss", "Net_PnL"])

    df["Month"] = pd.to_datetime(df["Exit Time"]).dt.to_period("M").astype(str)
    all_months = pd.period_range(end=pd.Timestamp.now(), periods=12, freq="M").astype(str)
    base = pd.DataFrame({"Month": all_months})

    summary = df.groupby("Month").agg(
        Total_Trades=("PnL per lot", "count"),
        Total_Profit=("PnL per lot", lambda x: x[x > 0].sum()),
        Total_Loss=("PnL per lot", lambda x: x[x < 0].sum()),
        Net_PnL=("PnL per lot", "sum")
    ).reset_index()

    full_summary = base.merge(summary, on="Month", how="left").fillna(0)
    full_summary["Total_Trades"] = full_summary["Total_Trades"].astype(int)
    return full_summary

def daily_pnl_summary(df):
    if df.empty or "Exit Time" not in df.columns:
        return pd.DataFrame(columns=["Day", "Total_Trades", "Total_Profit", "Total_Loss", "Net_PnL"])

    df["Day"] = pd.to_datetime(df["Exit Time"]).dt.date
    all_days = pd.date_range(end=pd.Timestamp.now(), periods=30).date
    base = pd.DataFrame({"Day": all_days})

    summary = df.groupby("Day").agg(
        Total_Trades=("PnL per lot", "count"),
        Total_Profit=("PnL per lot", lambda x: x[x > 0].sum()),
        Total_Loss=("PnL per lot", lambda x: x[x < 0].sum()),
        Net_PnL=("PnL per lot", "sum")
    ).reset_index()

    full_summary = base.merge(summary, on="Day", how="left").fillna(0)
    full_summary["Total_Trades"] = full_summary["Total_Trades"].astype(int)
    return full_summary
