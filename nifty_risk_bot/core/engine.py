"""
Main engine orchestrator for the Nifty Risk Engine.
"""

from ..data.fetcher import fetch_market_snapshot
from .sentiment import get_sentiment_score
from .scoring import calculate_score


def run_engine() -> tuple[dict, dict]:
    """
    Run the complete risk analysis engine.
    
    Returns:
        Tuple of (result, market_data) where:
        - result: Dictionary with score, risk level, recommendations
        - market_data: Raw market data used for analysis
    """
    # ---------------------------
    # 1. Fetch Market Data
    # ---------------------------
    data = fetch_market_snapshot()

    # ---------------------------
    # 2. Get Sentiment
    # ---------------------------
    sentiment_score = get_sentiment_score()

    # ---------------------------
    # 3. Event Risk (manual for now)
    # ---------------------------
    event_risk = False  # change to True if major event week

    # ---------------------------
    # 4. Calculate Score
    # ---------------------------
    result = calculate_score(data, sentiment_score, event_risk)

    return result, data
