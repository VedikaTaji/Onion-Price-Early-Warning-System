# Onion Price Early-Warning System for Farmers
**Final-year capstone prototype | Python, SARIMA, XGBoost, Streamlit | English + Marathi**

## 1. What this project does
The application reads daily onion modal prices for Lasalgaon APMC, aggregates them into weekly median prices, trains two forecasting approaches (SARIMA and XGBoost), blends their forecasts, and flags weeks where the forecast is outside a user-selected price band.

This is a decision-support prototype. It does **not** guarantee future prices and must not be presented as a buy/sell instruction.

## 2. Folder structure
```text
Onion_Price_Early_Warning_System/
├── app/
│   └── main.py                 # Streamlit bilingual dashboard
├── src/
│   ├── data.py                 # Agmarknet CSV normalization + weekly aggregation
│   ├── features.py             # Lag and rolling-window features
│   └── models.py               # SARIMA, XGBoost, blend and holdout evaluation
├── data/
│   ├── demo_synthetic_prices.csv
│   └── DATA_SOURCE_GUIDE.md
├── reports/
│   └── ETHICS_NOTE.md
├── tests/
│   └── test_data.py
├── requirements.txt
├── run_app.bat
└── README.md
```

## 3. Requirements
- Windows 10/11, macOS or Linux
- Python 3.10 or 3.11 recommended
- Internet connection for first-time package installation
- An Agmarknet CSV export for real forecasts

## 4. Run on Windows (VS Code / PowerShell)
Open the extracted folder in VS Code, then run:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app/main.py
```

If PowerShell blocks activation, run this once in the current terminal:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```
Then activate the environment again.

Alternative: double-click `run_app.bat`.

## 5. Obtain real Lasalgaon onion prices
1. Open the Government of India Agmarknet portal: https://agmarknet.gov.in/
2. Open the price/market price report or daily market arrivals and prices report.
3. Set State = Maharashtra, District = Nashik, Market = Lasalgaon, Commodity = Onion.
4. Select the longest useful date range available (preferably 1–2 years or more).
5. Export/download the report as CSV.
6. In the Streamlit sidebar, upload the CSV. The parser looks for date and modal price fields (common names include `Arrival_Date` and `Modal_Price`).
7. Check the first/last dates and values against the original portal report before interpreting the forecast.

**Important:** Portal layouts and download options can change. This project deliberately uses user-provided CSV upload instead of relying on an undocumented API or scraping workflow. Do not treat the included synthetic demo file as actual market data.

Dataset documentation: `data/DATA_SOURCE_GUIDE.md`.

## 6. Model methodology
### Data preparation
- Parse date and modal price columns from common Agmarknet CSV formats.
- Filter to Lasalgaon where a market column is available.
- Filter onion where a commodity column is available.
- Remove invalid dates and non-positive prices.
- Collapse multiple daily records to a daily median.
- Aggregate daily prices into Sunday-ending weekly medians to reduce noise.

### SARIMA
The baseline is SARIMA(1,1,1)(1,0,1,52), where 52 represents annual seasonality in weekly data. The model captures autocorrelation, differencing/trend and annual seasonal structure. A full seasonal cycle is preferable; with shorter datasets the seasonal component may be weakly identified.

### XGBoost
The tree-based model uses lagged weekly prices (1–8 weeks), 4- and 8-week rolling means, rolling standard deviation, week-of-year and month. It forecasts recursively for four weeks.

### Ensemble and alerts
The default ensemble is a 50:50 blend of SARIMA and XGBoost. This is a transparent starting point, not a statistically optimized weight. The user selects a lower and upper band in ₹/quintal. An alert appears when the ensemble point forecast is outside the band.

The app also shows the individual model outputs and their spread. Model spread is **not** a calibrated prediction interval. The backtest is chronological (last weeks held out), not a random split.

## 7. Evaluation
The app reports MAE and RMSE for a chronological holdout. Lower values indicate smaller errors on that particular holdout. For a serious study:
- Compare against naïve last-week and seasonal-naïve baselines.
- Use rolling-origin time-series cross-validation.
- Report MAE, RMSE and MAPE/sMAPE (avoid MAPE when actual prices are near zero).
- Test different SARIMA orders and ensemble weights on validation data only.
- Report results across multiple time windows, not only one split.
- Do not claim generalization from the synthetic demo dataset.

## 8. Ethics and responsible communication
Read `reports/ETHICS_NOTE.md`. Public price forecasts can influence market behaviour and could be misused for hoarding, coordinated withholding, speculative pressure or misinformation. Use aggregate market-level data, show source and timestamp, communicate uncertainty, and never promise a price direction.

## 9. Known limitations
- The baseline model uses price history only; it does not include rainfall, arrivals/volume, acreage, quality, transport, storage, exports, imports or policy changes.
- Forecasts may fail during weather shocks, crop disease, sudden arrivals, export restrictions or other structural breaks.
- Agmarknet data may contain missing dates, grade/variety differences, reporting delays and outliers.
- The current model-spread display is a disagreement diagnostic, not a formal confidence interval.
- The app is a prototype for learning and demonstration, not a commercial commodity advisory.

## 10. Run tests
```powershell
pytest -q
```

## 11. Suggested capstone presentation flow
1. Problem: farmers face uncertainty in deciding when and where to sell.
2. Data: daily Lasalgaon APMC modal prices from Agmarknet.
3. Pipeline: cleaning → daily median → weekly median → features.
4. Models: SARIMA + XGBoost → 50:50 ensemble.
5. Output: four-week forecast + configurable price-band alert.
6. Evaluation: chronological holdout MAE/RMSE.
7. Ethics: uncertainty, no hoarding facilitation, no guaranteed-price claims.

## 12. Academic integrity
Clearly state which dataset period was downloaded, the exact model configuration, test window and measured scores. Do not invent performance results. Replace the demo dataset with the official CSV before taking screenshots or reporting project results.
