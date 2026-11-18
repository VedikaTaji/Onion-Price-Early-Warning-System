# Ethics note: public agricultural price forecasts

## Intended benefit
A short-horizon market outlook may help farmers ask better questions about timing, transport, storage costs and alternative markets. It should complement, not replace, local knowledge, extension services and current mandi quotations.

## Misuse and foreseeable harms
1. **Hoarding and coordinated withholding:** traders or other actors could use a predicted increase to justify withholding stock, potentially reducing immediate supply and amplifying price volatility.
2. **Speculative pressure and misinformation:** a screenshot saying “onion prices will rise next week” may circulate without its date, source or uncertainty.
3. **Distress-sale manipulation:** a predicted fall could be selectively communicated to pressure farmers to sell quickly.
4. **False precision:** a single point forecast may appear certain even though weather, arrivals, quality, transport, policy and export conditions can change rapidly.
5. **Unequal access:** larger traders may have better connectivity and analytics access than small farmers.

## Safeguards in this prototype
- The dashboard identifies the data as synthetic when demo data is selected.
- Forecasts are described as estimates and not guaranteed prices.
- It shows SARIMA and XGBoost separately as well as their ensemble.
- The model spread is explicitly labelled as disagreement, not a confidence interval.
- Users choose their own price band; the app does not issue a buy/sell command.
- It uses market-level historical prices, not personal farmer data.

## Recommended safeguards before public deployment
- Display data source, last observation date, download timestamp and market/commodity filters beside every forecast.
- Add calibrated prediction intervals from rolling-origin residuals and publish empirical coverage.
- Add an explicit warning that model outputs must not be used to coordinate hoarding, collusion or supply withholding.
- Avoid push alerts with sensational wording such as “prices will crash” or “guaranteed rise”.
- Make the methodology, known limitations and model update history public.
- Consult farmer groups, APMC officials and agricultural extension experts before release.
- Monitor forecast errors and suspend alerts after major structural breaks or unreliable data updates.
- Do not collect personal farmer identity or location unless strictly necessary and protected.

## How to communicate uncertainty to farmers
Prefer: “Based on prices available through [date], the model estimates a weekly modal price near ₹X/quintal. The two models differ by ₹Y. Actual prices may be higher or lower due to arrivals, weather, quality, demand and policy changes. Please verify today's local mandi rate before deciding.”

Avoid: “The price will definitely reach ₹X” or “Do not sell now.”

## Conclusion
The system is an educational decision-support prototype. Responsible deployment requires calibrated uncertainty, transparent data provenance, local validation and stakeholder oversight. A forecast should inform a conversation, not dictate a farmer's decision.
