import pandas as pd
from src.data import normalize_agmarknet, weekly_series

def test_normalize_agmarknet():
    raw = pd.DataFrame({
        "Arrival_Date": pd.date_range("2024-01-01", periods=70).strftime("%d/%m/%Y"),
        "Market": ["Lasalgaon"]*70,
        "Commodity": ["Onion"]*70,
        "Modal_Price": [2000]*70
    })
    daily = normalize_agmarknet(raw)
    assert len(daily) == 70
    assert daily.modal_price.median() == 2000
    assert len(weekly_series(daily)) >= 9
