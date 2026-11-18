import numpy as np
import pandas as pd

def make_supervised(series: pd.Series, lags: int = 8):
    frame = pd.DataFrame({"y": series})
    for lag in range(1, lags + 1):
        frame[f"lag_{lag}"] = frame["y"].shift(lag)
    frame["rolling_mean_4"] = frame["y"].shift(1).rolling(4).mean()
    frame["rolling_std_4"] = frame["y"].shift(1).rolling(4).std()
    frame["rolling_mean_8"] = frame["y"].shift(1).rolling(8).mean()
    frame["week_of_year"] = frame.index.isocalendar().week.astype(int)
    frame["month"] = frame.index.month
    return frame.dropna()

def next_xgb_features(history: pd.Series, date: pd.Timestamp, lags: int = 8):
    values = list(history.iloc[-lags:].values[::-1])
    row = {f"lag_{i+1}": values[i] for i in range(lags)}
    row["rolling_mean_4"] = history.iloc[-4:].mean()
    row["rolling_std_4"] = history.iloc[-4:].std()
    row["rolling_mean_8"] = history.iloc[-8:].mean()
    row["week_of_year"] = int(date.isocalendar().week)
    row["month"] = int(date.month)
    return pd.DataFrame([row])
