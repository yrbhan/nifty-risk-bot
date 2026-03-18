import streamlit as st
from data_fetcher import fetch_market_snapshot
from sentiment import get_sentiment_score
from scoring_engine import calculate_score


# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(
    page_title="Nifty Risk Dashboard",
    layout="centered"
)

st.title("📊 Nifty Weekly Risk Dashboard")


# ---------------------------
# Fetch Data
# ---------------------------
data = fetch_market_snapshot()
sentiment_score = get_sentiment_score()
event_risk = False  # can automate later

result = calculate_score(data, sentiment_score, event_risk)


# ---------------------------
# Helper: Color Mapping
# ---------------------------
def get_color(score):
    if score >= 70:
        return "green"
    elif score >= 50:
        return "orange"
    else:
        return "red"


color = get_color(result["score"])


# ---------------------------
# Score Display
# ---------------------------
st.markdown(f"## Score: {result['score']}/100")
st.markdown(f"### Risk Level: :{color}[{result['risk']}]")

st.divider()


# ---------------------------
# Direction & Strength
# ---------------------------
st.markdown("### Market View")

st.write(f"**Direction:** {result['direction']}")
st.write(f"**Strength:** {result['strength']}")

st.divider()


# ---------------------------
# Trade Suggestion (HIGHLIGHT)
# ---------------------------
st.markdown("### 💡 Suggested Trade")

st.success(result["trade"])

st.divider()


# ---------------------------
# Recommendation
# ---------------------------
st.markdown("### Strategy Guidance")
st.info(result["action"])

st.divider()


# ---------------------------
# Reasons
# ---------------------------
st.markdown("### 🔍 Reasons")

for reason in result["reasons"]:
    st.write(f"- {reason}")

# ---------------------------
# Position Size
# ---------------------------
st.markdown("### 📦 Position Size")
st.warning(result["position_size"])

# ---------------------------
# Safety Warning
# ---------------------------
if result["warning"]:
    st.error(result["warning"])


# ---------------------------
# Market Snapshot
# ---------------------------
st.markdown("### 📊 Market Snapshot")

st.write(f"VIX Today: {data.get('vix_today')}")
st.write(f"VIX 3-day avg: {data.get('vix_3day_avg')}")
st.write(f"S&P 500 (1D): {data.get('sp500_1d_return')}%")
st.write(f"Nasdaq (1D): {data.get('nasdaq_1d_return')}%")
st.write(f"Nifty (3D): {data.get('nifty_3d_return')}%")