def calculate_score(data, sentiment_score=0, event_risk=False):

    score = 50
    reasons = []

    # ---------------------------
    # 1. VIX Trend
    # ---------------------------
    if data.get("vix_today") and data.get("vix_3day_avg"):
        if data["vix_today"] > data["vix_3day_avg"]:
            score -= 15
            reasons.append("VIX rising (high volatility)")
        else:
            score += 10
            reasons.append("VIX stable/falling")

    # ---------------------------
    # 2. Global Markets
    # ---------------------------
    sp500_ret = data.get("sp500_1d_return", 0)
    nasdaq_ret = data.get("nasdaq_1d_return", 0)

    if sp500_ret < -1.5 or nasdaq_ret < -2:
        score -= 15
        reasons.append("US markets falling sharply")
    elif sp500_ret > 1:
        score += 5
        reasons.append("US markets stable/positive")

    # ---------------------------
    # 3. Nifty Trend (3-day)
    # ---------------------------
    nifty_trend = data.get("nifty_3d_return", 0)

    if abs(nifty_trend) > 2:
        score -= 20
        reasons.append("Nifty trending strongly (danger for sellers)")
    else:
        score += 10
        reasons.append("Nifty range-bound (good for theta)")

    # ---------------------------
    # 4. Event Risk
    # ---------------------------
    if event_risk:
        score -= 20
        reasons.append("Major event this week")

    # ---------------------------
    # 5. News Sentiment
    # ---------------------------
    if sentiment_score < -0.3:
        score -= 10
        reasons.append("Negative news sentiment")
    elif sentiment_score > 0.3:
        score += 5
        reasons.append("Positive news sentiment")

    # ---------------------------
    # Direction Detection (MOVE HERE)
    # ---------------------------
    direction = "Neutral"
    strength = "Weak"

    if nifty_trend < -2:
        direction = "Bearish"
        strength = "Strong"
    elif nifty_trend < -1:
        direction = "Bearish"
        strength = "Weak"
    elif nifty_trend > 2:
        direction = "Bullish"
        strength = "Strong"
    elif nifty_trend > 1:
        direction = "Bullish"
        strength = "Weak"

    # Strengthen with global confirmation
    if direction == "Bearish" and sp500_ret < -1:
        reasons.append("Global confirmation of bearish trend")
    elif direction == "Bullish" and sp500_ret > 1:
        reasons.append("Global confirmation of bullish trend")

    # ---------------------------
    # Final Score Clamp
    # ---------------------------
    score = max(0, min(100, score))

    # ---------------------------
    # Strategy Recommendation
    # ---------------------------
    if score >= 70:
        action = "Full iron condor / strangle OK"
        trade = "Sell both call and put (theta decay)"

    elif score >= 50:
        action = "Reduce position size, use hedges"
        trade = "Light iron condor with hedges"

    elif score >= 30:
        action = "Directional trade only"

        if direction == "Bullish":
            trade = "Sell put spreads (bullish bias)"
        elif direction == "Bearish":
            trade = "Sell call spreads (bearish bias)"
        else:
            trade = "Wait or trade very small size"

    else:
        action = "Avoid trading this week"
        trade = "No trade"

    # ---------------------------
    # Risk Tag
    # ---------------------------
    if score >= 70:
        risk = "Low"
    elif score >= 50:
        risk = "Moderate"
    elif score >= 30:
        risk = "High"
    else:
        risk = "Very High"

    # ---------------------------
    # Position Sizing
    # ---------------------------
    if score >= 70:
        size = "Full size (100%)"
    elif score >= 50:
        size = "Medium size (60-70%)"
    elif score >= 30:
        size = "Small size (30-50%)"
    else:
        size = "No trade"

    # ---------------------------
    # Safety Warning
    # ---------------------------
    warning = None

    if score < 50 and strength == "Strong":
        warning = "Avoid naked selling. Use hedged spreads only."

    return {
        "score": score,
        "action": action,
        "direction": direction,
        "strength": strength,
        "risk": risk,
        "trade": trade,
        "position_size": size,
        "reasons": reasons,
        "warning": warning
    }