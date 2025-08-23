import pandas as pd
import datetime

def fetch_live_ohlc(symbol):
    # Placeholder: Replace with Groww or SmartAPI fetcher
    # Simulate 100 candles of synthetic OHLC for now
    import numpy as np
    rng = pd.date_range(end=datetime.datetime.now(), periods=100, freq="5min")
    open_prices = np.random.uniform(19000, 20000, size=100)
    close_prices = open_prices + np.random.uniform(-50, 50, size=100)
    high_prices = np.maximum(open_prices, close_prices) + np.random.uniform(5, 20, size=100)
    low_prices = np.minimum(open_prices, close_prices) - np.random.uniform(5, 20, size=100)

    df = pd.DataFrame({
        "timestamp": rng,
        "open": open_prices,
        "high": high_prices,
        "low": low_prices,
        "close": close_prices
    })
    return df

def disparity_index_optimized(df, short=9, long=20, lower_thresh=-3, upper_thresh=4):
    df["EMA_short"] = df["close"].ewm(span=short, adjust=False).mean()
    df["EMA_long"] = df["close"].ewm(span=long, adjust=False).mean()
    df["Disparity"] = ((df["close"] - df["EMA_long"]) / df["EMA_long"]) * 100
    df["Signal"] = ""
    df.loc[df["Disparity"] < lower_thresh, "Signal"] = "BUY"
    df.loc[df["Disparity"] > upper_thresh, "Signal"] = "SELL"
    df["Price"] = df["close"].round(2)
    return df

def auto_trade_executor(df, symbol):
    lot_sizes = {
        "NIFTY": 75,
        "BANKNIFTY": 30
    }
    lot_size = lot_sizes.get(symbol, 1)

    trades = []
    position = None
    entry_price = None
    entry_time = None
    cumulative_pnl = 0

    for _, row in df.iterrows():
        signal = row["Signal"]
        price = row["Price"]
        time = row["timestamp"]

        if signal == "BUY" and position is None:
            position = "LONG"
            entry_price = price
            entry_time = time

        elif signal == "SELL" and position == "LONG":
            exit_price = price
            exit_time = time
            pnl = round((exit_price - entry_price) * lot_size, 2)
            cumulative_pnl += pnl

            trades.append({
                "Symbol": symbol,
                "Entry Time": entry_time,
                "Entry Price": entry_price,
                "Exit Time": exit_time,
                "Exit Price": exit_price,
                "PnL per lot": pnl,
                "Cumulative PnL": cumulative_pnl,
                "Lot Size": lot_size
            })

            position = None
            entry_price = None
            entry_time = None

    return pd.DataFrame(trades)

def monthly_pnl_summary(paired_df):
    df = paired_df.copy()
    df["Month"] = df["Exit Time"].dt.to_period("M").astype(str)
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

def daily_pnl_summary(paired_df):
    df = paired_df.copy()
    df["Day"] = df["Exit Time"].dt.date
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

def reasoning_panel(df):
    latest = df.iloc[-1]
    return {
        "Disparity": round(latest["Disparity"], 2),
        "EMA_short": round(latest["EMA_short"], 2),
        "EMA_long": round(latest["EMA_long"], 2),
        "Signal": latest["Signal"]
    }
