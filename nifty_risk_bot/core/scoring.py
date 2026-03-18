"""
Scoring engine for the Nifty Risk Engine.
"""

from typing import Dict, Any


def calculate_score(data: Dict[str, Any], sentiment_score: float = 0, event_risk: bool = False) -> Dict[str, Any]:
    """
    Calculate risk score based on market data, sentiment, and event risk.
    
    Args:
        data: Market data dictionary with indicators
        sentiment_score: Sentiment analysis score [-1, 1]
        event_risk: Boolean indicating major event risk
        
    Returns:
        Dictionary with score, risk level, direction, and recommendations
    """
    score = 50
    reasons = []

    # ---------------------------
    # 1. VIX Trend
    # ---------------------------
    if data.get("vix_today") and data.get("vix_3day_avg"):
        if data["vix_today"] > data["vix_3day_avg"]:
            score -= 20
            reasons.append("VIX rising (high volatility)")
        else:
            score += 15
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
        score -= 25
        reasons.append("Nifty trending strongly (danger for sellers)")
    else:
        score += 10
        reasons.append("Nifty range-bound (good for theta)")

    # ---------------------------
    # 3B. Recent Shock Detection
    # ---------------------------
    nifty_1d = data.get("nifty_1d_return", 0) or 0

    if abs(nifty_1d) > 1.5:
        score -= 10
        reasons.append("Recent sharp move (unstable market)")

    # ---------------------------
    # 3C. GIFT NIFTY Pre-Market Movement
    # ---------------------------
    gift_nifty_change = data.get("gift_nifty_change_pct", 0)
    
    if gift_nifty_change is not None:
        if abs(gift_nifty_change) > 1.5:
            score -= 20
            reasons.append(f"Large pre-market gap ({gift_nifty_change:+.1f}%)")
        elif abs(gift_nifty_change) > 0.8:
            score -= 10
            reasons.append(f"Moderate pre-market movement ({gift_nifty_change:+.1f}%)")
        elif abs(gift_nifty_change) > 0.3:
            score -= 5
            reasons.append(f"Mild pre-market movement ({gift_nifty_change:+.1f}%)")
        else:
            score += 5
            reasons.append("Pre-market stable")
    else:
        reasons.append("GIFT NIFTY data unavailable")

    # ---------------------------
    # 4. Event Risk
    # ---------------------------
    if event_risk:
        score -= 20
        reasons.append("Major event this week")

    # ---------------------------
    # 5. News Sentiment
    # ---------------------------
    if sentiment_score < -0.4:
        score -= 15
        reasons.append("Strong negative sentiment (risk event)")
    elif sentiment_score > 0.4:
        score += 5
        reasons.append("Strong positive sentiment")

    # ---------------------------
    # Direction Detection
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

    # Adjust direction based on GIFT NIFTY pre-market movement
    gift_nifty_change = data.get("gift_nifty_change_pct", 0)
    if gift_nifty_change is not None:
        if abs(gift_nifty_change) > 0.5:  # Only consider meaningful moves
            gift_direction = "Bearish" if gift_nifty_change < -0.5 else "Bullish"
            gift_strength = "Strong" if abs(gift_nifty_change) > 1.5 else "Weak"
            
            # If GIFT NIFTY shows strong directional bias, override or strengthen
            if gift_strength == "Strong":
                direction = gift_direction
                strength = gift_strength
                reasons.append(f"Strong pre-market {gift_direction.lower()} bias")
            elif direction == "Neutral":
                direction = gift_direction
                strength = gift_strength
                reasons.append(f"Pre-market {gift_direction.lower()} bias")

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
