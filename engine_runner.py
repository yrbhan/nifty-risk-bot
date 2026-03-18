def run_engine():
    from data_fetcher import fetch_market_snapshot
    from sentiment import get_sentiment_score
    from scoring_engine import calculate_score

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
    event_risk = False # change to True if major event week


    return calculate_score(data, sentiment_score, event_risk), data