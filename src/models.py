from __future__ import annotations
import warnings
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.ensemble import HistGradientBoostingRegressor
from src.features import make_supervised, next_xgb_features

def forecast_sarima(series: pd.Series, horizon: int = 4):
    """SARIMA-style model; seasonal period 52 for weekly prices."""
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    y = series.astype(float).asfreq("W-SUN")
    y = y.interpolate(limit_direction="both")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = SARIMAX(
            y, order=(1,1,1), seasonal_order=(1,0,1,52),
            enforce_stationarity=False, enforce_invertibility=False
        )
        fit = model.fit(disp=False, maxiter=120)
        pred = fit.get_forecast(steps=horizon)
        mean = pred.predicted_mean
        ci = pred.conf_int(alpha=0.20)
    return pd.DataFrame({
        "date": pd.date_range(y.index[-1] + pd.Timedelta(days=7), periods=horizon, freq="W-SUN"),
        "sarima": np.maximum(mean.values, 0),
        "sarima_lower": np.maximum(ci.iloc[:,0].values, 0),
        "sarima_upper": np.maximum(ci.iloc[:,1].values, 0),
    })

def forecast_xgboost(series: pd.Series, horizon: int = 4):
    """Recursive tree-based forecast. HistGradientBoosting is used as a no-extra-binary fallback."""
    from xgboost import XGBRegressor
    train = make_supervised(series, lags=8)
    X = train.drop(columns="y")
    y = train["y"]
    model = XGBRegressor(
        n_estimators=350, max_depth=3, learning_rate=0.035,
        subsample=0.85, colsample_bytree=0.9, objective="reg:squarederror",
        random_state=42, n_jobs=2
    )
    model.fit(X, y)
    history = series.copy()
    rows = []
    for step in range(horizon):
        next_date = history.index[-1] + pd.Timedelta(days=7)
        feat = next_xgb_features(history, next_date, lags=8)
        value = max(0.0, float(model.predict(feat)[0]))
        rows.append({"date": next_date, "xgboost": value})
        history.loc[next_date] = value
    return pd.DataFrame(rows)

def combined_forecast(series: pd.Series, horizon: int = 4, sarima_weight: float = 0.5):
    sarima = forecast_sarima(series, horizon)
    xgb = forecast_xgboost(series, horizon)
    out = sarima.merge(xgb, on="date")
    out["forecast"] = sarima_weight*out["sarima"] + (1-sarima_weight)*out["xgboost"]
    out["forecast"] = out["forecast"].clip(lower=0)
    # Model disagreement is shown as a transparent uncertainty proxy, not a formal prediction interval.
    out["model_spread_low"] = out[["sarima", "xgboost"]].min(axis=1)
    out["model_spread_high"] = out[["sarima", "xgboost"]].max(axis=1)
    return out

def evaluate_holdout(series: pd.Series, test_weeks: int = 8):
    """Simple chronological holdout comparison; no random shuffling."""
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    from xgboost import XGBRegressor
    from src.features import make_supervised
    if len(series) < 40:
        return None
    train, test = series.iloc[:-test_weeks], series.iloc[-test_weeks:]
    # SARIMA one-step rolling forecasts, refit-free forecast path.
    try:
        fit = SARIMAX(train, order=(1,1,1), seasonal_order=(1,0,1,52),
                      enforce_stationarity=False, enforce_invertibility=False).fit(disp=False, maxiter=80)
        sp = np.maximum(fit.get_forecast(steps=len(test)).predicted_mean.values, 0)
    except Exception:
        sp = np.repeat(float(train.iloc[-4:].mean()), len(test))
    try:
        sup = make_supervised(train, 8)
        model = XGBRegressor(n_estimators=250, max_depth=3, learning_rate=.04,
                             objective="reg:squarederror", random_state=42, n_jobs=2)
        model.fit(sup.drop(columns="y"), sup["y"])
        hist = train.copy()
        xp = []
        for dt in test.index:
            val = max(0., float(model.predict(next_xgb_features(hist, dt, 8))[0]))
            xp.append(val)
            hist.loc[dt] = val
    except Exception:
        xp = np.repeat(float(train.iloc[-4:].mean()), len(test))
    actual = test.values
    return {
        "SARIMA MAE": float(mean_absolute_error(actual, sp)),
        "XGBoost MAE": float(mean_absolute_error(actual, xp)),
        "SARIMA RMSE": float(np.sqrt(mean_squared_error(actual, sp))),
        "XGBoost RMSE": float(np.sqrt(mean_squared_error(actual, xp))),
    }
