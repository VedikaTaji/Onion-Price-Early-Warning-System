from __future__ import annotations
import pandas as pd
import numpy as np
from pathlib import Path

DATE_CANDIDATES = ["arrival_date", "date", "reported_date", "Date", "Arrival Date"]
PRICE_CANDIDATES = ["modal_price", "modal price", "Modal Price", "modal", "price", "Modal_Price"]
MARKET_CANDIDATES = ["market", "Market", "market_name", "Market Name"]
COMMODITY_CANDIDATES = ["commodity", "Commodity"]
VARIETY_CANDIDATES = ["variety", "Variety"]
MIN_CANDIDATES = ["min_price", "Min Price", "minimum_price"]
MAX_CANDIDATES = ["max_price", "Max Price", "maximum_price"]

def _find_column(columns, candidates):
    lookup = {str(c).strip().lower(): c for c in columns}
    for candidate in candidates:
        if candidate.lower() in lookup:
            return lookup[candidate.lower()]
    for c in columns:
        cl = str(c).strip().lower()
        if any(x.lower() in cl for x in candidates):
            return c
    return None

def normalize_agmarknet(df: pd.DataFrame, market_filter: str = "Lasalgaon") -> pd.DataFrame:
    """Normalize common Agmarknet CSV exports to date + modal_price columns."""
    if df.empty:
        raise ValueError("The uploaded dataset is empty.")
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    date_col = _find_column(df.columns, DATE_CANDIDATES)
    price_col = _find_column(df.columns, PRICE_CANDIDATES)
    market_col = _find_column(df.columns, MARKET_CANDIDATES)
    commodity_col = _find_column(df.columns, COMMODITY_CANDIDATES)

    if date_col is None or price_col is None:
        raise ValueError(
            "Could not identify date and modal-price columns. Expected columns similar to "
            "'Arrival_Date' and 'Modal_Price'. See README for supported formats."
        )

    if market_col and market_filter:
        mask = df[market_col].astype(str).str.contains(market_filter, case=False, na=False)
        if mask.any():
            df = df.loc[mask].copy()

    if commodity_col:
        mask = df[commodity_col].astype(str).str.contains("onion", case=False, na=False)
        if mask.any():
            df = df.loc[mask].copy()

    out = pd.DataFrame()
    out["date"] = pd.to_datetime(df[date_col], errors="coerce", dayfirst=True)
    out["modal_price"] = pd.to_numeric(
        df[price_col].astype(str).str.replace(",", "", regex=False).str.replace("₹", "", regex=False),
        errors="coerce"
    )
    min_col = _find_column(df.columns, MIN_CANDIDATES)
    max_col = _find_column(df.columns, MAX_CANDIDATES)
    if min_col:
        out["min_price"] = pd.to_numeric(df[min_col], errors="coerce")
    if max_col:
        out["max_price"] = pd.to_numeric(df[max_col], errors="coerce")

    out = out.dropna(subset=["date", "modal_price"])
    out = out[out["modal_price"] > 0]
    out = out.sort_values("date")
    # Multiple varieties/grades may occur on one date: daily median reduces duplicate influence.
    out = out.groupby("date", as_index=False).agg(
        modal_price=("modal_price", "median"),
        **({"min_price": ("min_price", "median")} if "min_price" in out else {}),
        **({"max_price": ("max_price", "median")} if "max_price" in out else {})
    )
    if len(out) < 40:
        raise ValueError(f"Only {len(out)} usable daily observations found. Upload at least 40 days; 1–2 years is preferable.")
    return out.reset_index(drop=True)

def weekly_series(daily: pd.DataFrame) -> pd.Series:
    s = daily.set_index("date")["modal_price"].sort_index()
    # Weekly median is robust to outlier daily arrivals/prices.
    weekly = s.resample("W-SUN").median().dropna()
    weekly.name = "price"
    if len(weekly) < 20:
        raise ValueError("At least 20 weekly observations are required for forecasting.")
    return weekly

def make_demo_data(days: int = 900, seed: int = 7) -> pd.DataFrame:
    """Clearly synthetic demonstration data. Never use it for real farmer decisions."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=days, freq="D")
    t = np.arange(days)
    seasonal = 450 * np.sin(2*np.pi*t/365.25) + 140*np.sin(2*np.pi*t/30.4)
    trend = 2.2*t/days*250
    noise = rng.normal(0, 170, days)
    price = np.clip(2200 + seasonal + trend + noise, 500, None)
    return pd.DataFrame({"date": dates, "modal_price": price.round(0)})

def load_demo_data() -> pd.DataFrame:
    path = Path(__file__).resolve().parents[1] / "data" / "demo_synthetic_prices.csv"
    return pd.read_csv(path, parse_dates=["date"])
