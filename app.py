import streamlit as st
from nifty_risk_bot.core.engine import run_engine


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
st.markdown("### 🔍 Key Risk Factors (Reasons for safety score value and risk level)")

# Create a more prominent reasons display
reasons_container = st.container()

with reasons_container:
    for i, reason in enumerate(result["reasons"], 1):
        # Use different styling based on reason type
        reason_lower = reason.lower()
        
        if (any(keyword in reason_lower for keyword in ["high", "large", "sharp", "danger", "risk event", "major event", "negative", "unstable"]) or
            "strong negative sentiment" in reason_lower or
            "trending strongly" in reason_lower):
            st.error(f"🚨 {reason}")
        elif (any(keyword in reason_lower for keyword in ["moderate", "falling", "mild"]) or
              "pre-market movement" in reason_lower):
            st.warning(f"⚠️ {reason}")
        elif (any(keyword in reason_lower for keyword in ["stable", "positive", "range-bound", "good for theta"]) or
              "strong positive sentiment" in reason_lower or
              "global confirmation" in reason_lower):
            st.success(f"✅ {reason}")
        else:
            st.info(f"📊 {reason}")
        
        # Add spacing between reasons
        if i < len(result["reasons"]):
            st.write("")

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

# GIFT NIFTY Section
st.markdown("### 🌍 Pre-Market (GIFT NIFTY)")
gift_nifty_current = data.get('gift_nifty_current')
gift_nifty_change = data.get('gift_nifty_change_pct')
gift_nifty_close = data.get('gift_nifty_close_value')

if gift_nifty_current is not None:
    st.write(f"GIFT NIFTY Current: {gift_nifty_current}")
    st.write(f"GIFT NIFTY Change: {gift_nifty_change:+.2f}%")
    st.write(f"Last NIFTY Close: {gift_nifty_close}")
    
    # Visual indicator for pre-market movement
    if gift_nifty_change is not None:
        if abs(gift_nifty_change) > 1.5:
            st.error(f"🚨 Large pre-market gap: {gift_nifty_change:+.2f}%")
        elif abs(gift_nifty_change) > 0.8:
            st.warning(f"⚠️ Moderate pre-market movement: {gift_nifty_change:+.2f}%")
        elif abs(gift_nifty_change) > 0.3:
            st.info(f"📊 Mild pre-market movement: {gift_nifty_change:+.2f}%")
        else:
            st.success(f"✅ Pre-market stable: {gift_nifty_change:+.2f}%")
else:
    st.warning("📡 GIFT NIFTY data unavailable")