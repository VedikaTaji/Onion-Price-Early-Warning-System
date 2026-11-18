import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
import pandas as pd
import numpy as np
from src.data import normalize_agmarknet, weekly_series, load_demo_data
from src.models import combined_forecast, evaluate_holdout

st.set_page_config(page_title="Onion Price Early-Warning System", page_icon="🧅", layout="wide")

TEXT = {
 "English": {
  "title":"Onion Price Early-Warning System",
  "subtitle":"Weekly price outlook for Lasalgaon APMC • Decision support, not a guarantee",
  "upload":"Upload Agmarknet CSV",
  "demo":"Use synthetic demo data",
  "market":"Market filter",
  "band":"Alert price band (₹/quintal)",
  "low":"Lower threshold",
  "high":"Upper threshold",
  "run":"Generate forecast",
  "history":"Historical weekly modal price",
  "forecast":"Next 4 weekly forecasts",
  "alert":"Price-band alert",
  "ethics":"Ethics & responsible use",
  "note":"Forecasts are estimates. Confirm today's mandi price and local conditions before making a sale, storage or transport decision.",
  "noalert":"No forecast point crosses your selected band.",
  "above":"Forecast crosses the upper threshold",
  "below":"Forecast falls below the lower threshold",
  "uploadhelp":"Use an Agmarknet CSV containing Arrival_Date and Modal_Price (column names may vary).",
  "source":"Data source",
  "source_text":"Agmarknet / Directorate of Marketing & Inspection (DMI). Upload a downloaded Lasalgaon onion price CSV. The demo data is synthetic.",
  "metrics":"Backtest (last 8 weeks)",
  "uncertainty":"Model spread (SARIMA vs XGBoost) is a simple disagreement indicator, not a calibrated confidence interval.",
  "ethics_text":"Public forecasts can be misused to coordinate hoarding, manipulate expectations or pressure farmers into distress sales. This app is a decision-support prototype, not a trading signal. Publish the data date, source, model limitations and uncertainty alongside every forecast. Do not identify or target individual farmers. Avoid claims such as “price will definitely rise”. Use ranges, explain that weather, arrivals, policy and demand can change outcomes, and encourage farmers to verify local mandi rates and consult trusted market/extension sources. Aggregated forecasts should not be used to coordinate storage or withholding supply.",
  },
 "मराठी": {
  "title":"कांदा बाजारभाव पूर्वसूचना प्रणाली",
  "subtitle":"लासलगाव APMC साठी साप्ताहिक भावाचा अंदाज • निर्णयासाठी मदत, हमी नाही",
  "upload":"Agmarknet CSV अपलोड करा",
  "demo":"डेमो डेटा वापरा",
  "market":"बाजार फिल्टर",
  "band":"इशारा भाव मर्यादा (₹/क्विंटल)",
  "low":"किमान मर्यादा",
  "high":"कमाल मर्यादा",
  "run":"अंदाज तयार करा",
  "history":"मागील साप्ताहिक सरासरी बाजारभाव",
  "forecast":"पुढील ४ आठवड्यांचा अंदाज",
  "alert":"भाव मर्यादेबाबत सूचना",
  "noalert":"तुम्ही निवडलेल्या मर्यादेबाहेर कोणताही अंदाज नाही.",
  "above":"अंदाज कमाल मर्यादेपेक्षा जास्त आहे",
  "below":"अंदाज किमान मर्यादेपेक्षा कमी आहे",
  "uploadhelp":"Arrival_Date आणि Modal_Price असलेली Agmarknet CSV फाइल वापरा.",
  "source":"डेटा स्रोत",
  "source_text":"Agmarknet / DMI. लासलगाव कांदा बाजारभावाची CSV फाइल अपलोड करा. डेमो डेटा कृत्रिम आहे.",
  "metrics":"मागील ८ आठवड्यांची चाचणी",
  "uncertainty":"SARIMA आणि XGBoost मधील फरक हा अनिश्चिततेचा साधा संकेत आहे; तो प्रमाणित विश्वास-अंतर नाही.",
  "ethics":"नैतिकता आणि जबाबदार वापर",
  "note":"अंदाज हा केवळ अंदाज आहे. विक्री, साठवण किंवा वाहतुकीचा निर्णय घेण्यापूर्वी आजचा बाजारभाव आणि स्थानिक परिस्थिती तपासा.",
  "ethics_text":"सार्वजनिक अंदाजाचा वापर साठेबाजी, बाजारभावाबद्दल चुकीच्या अपेक्षा निर्माण करणे किंवा शेतकऱ्यांवर दबाव आणण्यासाठी होऊ शकतो. हे साधन केवळ निर्णय सहाय्यक आहे; व्यापाराचा सल्ला नाही. प्रत्येक अंदाजासोबत डेटा तारीख, स्रोत, मर्यादा आणि अनिश्चितता दाखवा. कोणत्याही वैयक्तिक शेतकऱ्याची ओळख उघड करू नका. भाव नक्की वाढेल असे सांगू नका. हवामान, आवक, सरकारी धोरण आणि मागणीमुळे भाव बदलू शकतात. स्थानिक बाजारभावाची खात्री करा.",
 }
}

lang = st.sidebar.selectbox("Language / भाषा", ["English", "मराठी"])
t = TEXT[lang]
st.title("🧅 " + t["title"])
st.caption(t["subtitle"])

with st.sidebar:
    st.header("⚙️ Settings / सेटिंग्ज")
    uploaded = st.file_uploader(t["upload"], type=["csv"])
    st.caption(t["uploadhelp"])
    market = st.text_input(t["market"], "Lasalgaon")
    st.subheader(t["band"])
    low = st.number_input(t["low"], min_value=0, value=1500, step=100)
    high = st.number_input(t["high"], min_value=0, value=3000, step=100)
    if low >= high:
        st.warning("Lower threshold must be less than upper threshold.")
    use_demo = st.checkbox(t["demo"], value=uploaded is None)
    run = st.button(t["run"], type="primary", use_container_width=True)

st.info(t["note"])
st.caption(t["source_text"])

if run or "forecast_data" not in st.session_state:
    try:
        if uploaded is not None:
            raw = pd.read_csv(uploaded)
            daily = normalize_agmarknet(raw, market_filter=market)
            data_label = "Uploaded Agmarknet data"
        elif use_demo:
            daily = load_demo_data()
            data_label = "SYNTHETIC DEMO DATA — NOT REAL MARKET PRICES"
        else:
            st.warning("Upload a CSV or select synthetic demo data.")
            st.stop()

        weekly = weekly_series(daily)
        with st.spinner("Training SARIMA and XGBoost models..."):
            fc = combined_forecast(weekly, horizon=4)
        st.session_state["daily"] = daily
        st.session_state["weekly"] = weekly
        st.session_state["forecast_data"] = fc
        st.session_state["data_label"] = data_label
        st.session_state["band"] = (low, high)
    except Exception as e:
        st.error(f"Could not create forecast: {e}")
        st.stop()

daily = st.session_state["daily"]
weekly = st.session_state["weekly"]
fc = st.session_state["forecast_data"]
st.warning(st.session_state["data_label"])

c1,c2,c3,c4 = st.columns(4)
c1.metric("Latest weekly median", f"₹{weekly.iloc[-1]:,.0f}/qtl")
c2.metric("Forecast week 1", f"₹{fc.forecast.iloc[0]:,.0f}/qtl")
c3.metric("Forecast week 4", f"₹{fc.forecast.iloc[-1]:,.0f}/qtl")
c4.metric("History", f"{len(weekly)} weeks")

st.subheader(t["history"])
st.line_chart(weekly.rename("Observed price"))
st.subheader(t["forecast"])
chart = fc.set_index("date")[["forecast","sarima","xgboost"]]
st.line_chart(chart)
display = fc.copy()
display["date"] = display["date"].dt.strftime("%d %b %Y")
for col in ["sarima","xgboost","forecast","model_spread_low","model_spread_high"]:
    display[col] = display[col].round(0)
st.dataframe(display, use_container_width=True, hide_index=True)
st.caption(t["uncertainty"])

st.subheader(t["alert"])
if low >= high:
    st.error("Please set a valid price band.")
else:
    crossed = fc[(fc["forecast"] < low) | (fc["forecast"] > high)]
    if crossed.empty:
        st.success(t["noalert"])
    else:
        for _, row in crossed.iterrows():
            direction = t["above"] if row["forecast"] > high else t["below"]
            st.warning(f"{row['date'].strftime('%d %b %Y')}: {direction} — ₹{row['forecast']:,.0f}/qtl")

st.subheader(t["metrics"])
if len(weekly) >= 40:
    with st.spinner("Running chronological holdout evaluation..."):
        try:
            metrics = evaluate_holdout(weekly, test_weeks=min(8, max(4, len(weekly)//8)))
            if metrics:
                st.dataframe(pd.DataFrame([{"Metric": k, "Value": round(v,2)} for k,v in metrics.items()]), hide_index=True)
        except Exception as e:
            st.caption(f"Backtest unavailable for this dataset: {e}")
else:
    st.caption("Add more history (ideally 1–2 years) for a meaningful backtest.")

with st.expander(t["ethics"], expanded=True):
    st.write(t["ethics_text"])
    st.markdown("**Limitations:** price-only models cannot fully account for rainfall, crop arrivals, storage capacity, export restrictions, transport costs, quality/grade mix or sudden policy changes. Forecast accuracy can deteriorate during shocks.")

st.caption("Prototype for educational use • Prices in Indian Rupees per quintal (₹/qtl) • Not financial or trading advice")
