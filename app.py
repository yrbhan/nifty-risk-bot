import streamlit as st
from engine_runner import run_engine


# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(
    page_title="Nifty Risk Dashboard",
    layout="centered"
)

st.title("📊 Nifty Weekly Risk Dashboard")


# ---------------------------
# Run Engine to calculate score and get data
# ---------------------------
result, data = run_engine()


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
st.markdown(f"## Safety Score: {result['score']}/100")

if result["score"] >= 70:
    st.success("🟢 Good for option selling (low risk)")
elif result["score"] >= 50:
    st.warning("🟡 Moderate risk – trade carefully")
else:
    st.error("🔴 High risk – avoid aggressive selling")

st.markdown("### 🧠 What This Score Means")

st.info(
    "This score indicates how safe it is to SELL weekly options (theta strategies). "
    "Higher score = safer for option sellers. Lower score = higher risk of large moves."
)
    
st.markdown("### ⚠️ Risk Level (for Option Sellers)")

st.markdown(
    f":{color}[{result['risk']}] — Risk of large market moves hurting short option positions"
)

st.divider()

st.markdown("### 📌 Why This Matters")

st.write(
    "Short option strategies work best in stable, range-bound markets. "
    "Sudden trends or volatility spikes can lead to large losses."
)


# ---------------------------
# Direction & Strength
# ---------------------------
st.markdown("### Market View")

if result["direction"] == "Bullish":
    st.success("Direction: Bullish")
elif result["direction"] == "Bearish":
    st.error("Direction: Bearish")
else:
    st.info("Direction: Neutral")
st.write(f"**Strength:** {result['strength']}")

st.divider()


# ---------------------------
# Trade Suggestion (HIGHLIGHT)
# ---------------------------
st.markdown("### 💡 Suggested Trade")

st.markdown("### 💡 Suggested Trade (Based on Current Risk)")

st.success(result["trade"])

st.caption(
    "This suggestion is based on volatility, trend, and global market conditions."
)

st.divider()


# ---------------------------
# Recommendation
# ---------------------------
st.markdown("### Strategy Guidance (What You Should Do)")
st.info(result["action"])

st.divider()


# ---------------------------
# Reasons
# ---------------------------
st.markdown("### 🔍 Reasons")

# for reason in result["reasons"]:
#     st.write(f"- {reason}")

for reason in result["reasons"]:
    st.warning("\n".join(result["reasons"]))

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
st.write(f"S&P 500 (3D): {data.get('sp500_3d_return')}%")
st.write(f"Nasdaq (1D): {data.get('nasdaq_1d_return')}%")
st.write(f"Nasdaq (3D): {data.get('nasdaq_3d_return')}%")
st.write(f"Nifty (1D): {data.get('nifty_1d_return')}%")
st.write(f"Nifty (3D): {data.get('nifty_3d_return')}%")