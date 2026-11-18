# Dataset source and preparation guide

## Primary source
**Agmarknet — Directorate of Marketing & Inspection (DMI), Government of India**
Portal: https://agmarknet.gov.in/

Target slice:
- State: Maharashtra
- District: Nashik
- Market/APMC: Lasalgaon
- Commodity: Onion
- Price field: Modal Price (₹ per quintal)
- Date: Arrival Date / reported date

Download the daily price report as CSV. Prefer at least 1–2 years; 3–5 years is useful if the data definitions remain consistent.

## CSV fields used
| Canonical field | Common source column names | Required |
|---|---|---|
| date | Arrival_Date, Arrival Date, date, reported_date | Yes |
| modal_price | Modal_Price, Modal Price, modal_price, price | Yes |
| market | Market, Market Name, market_name | No, but recommended |
| commodity | Commodity | No, but recommended |
| min_price | Min Price, min_price | No |
| max_price | Max Price, max_price | No |

The loader handles common capitalization and spacing differences. If your export uses different headings, rename the relevant columns to `Arrival_Date` and `Modal_Price` in Excel and save as CSV.

## Data quality checks
- Verify market and commodity are Lasalgaon and Onion.
- Confirm prices are ₹/quintal, not ₹/kg.
- Check date range and duplicate dates.
- Check missing dates; the weekly aggregation uses observed daily records only.
- Do not mix different units or markets.
- Keep the original downloaded file unchanged for reproducibility.

## Demo data warning
`demo_synthetic_prices.csv` is randomly generated synthetic data for checking that the dashboard and modelling pipeline run. It is **not** an Agmarknet extract and must never be cited as real market data.
