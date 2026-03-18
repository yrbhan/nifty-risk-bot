from data_fetcher import fetch_market_snapshot
from sentiment import get_sentiment_score
from scoring_engine import calculate_score


def main():
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
    result = calculate_score(
        data=data,
        sentiment_score=sentiment_score,
        event_risk=event_risk
    )

    # ---------------------------
    # 5. Print Output
    # ---------------------------
    print("\n===== MARKET RISK ANALYSIS =====")
    print(f"Score: {result['score']}/100")
    print(f"Risk Level: {result['risk']}")
    print(f"Recommendation: {result['action']}")
    print(f"Market Direction: {result['direction']}")
    print(f"Trend Strength: {result['strength']}")
    print(f"Suggested Trade: {result['trade']}")
    print("\nReasons:")

    for reason in result["reasons"]:
        print(f"- {reason}")


if __name__ == "__main__":
    main()