"""
Sentiment analysis module for the Nifty Risk Engine.
"""

from __future__ import annotations

from dataclasses import dataclass

from textblob import TextBlob

from ..data.fetcher import NewsItem, fetch_google_news_rss


@dataclass(frozen=True)
class SentimentSummary:
    """Summary of news sentiment analysis."""
    polarity_mean: float  # [-1, 1]
    polarity_std: float
    n_items: int


def headline_sentiment(title: str) -> float:
    """
    Simple polarity score in [-1, 1] using TextBlob.
    """
    t = (title or "").strip()
    if not t:
        return 0.0
    return float(TextBlob(t).sentiment.polarity)


def summarize_news_sentiment(items: list[NewsItem]) -> SentimentSummary:
    """Summarize sentiment across multiple news items."""
    if not items:
        return SentimentSummary(polarity_mean=0.0, polarity_std=0.0, n_items=0)

    vals = [headline_sentiment(i.title) for i in items if (i.title or "").strip()]
    if not vals:
        return SentimentSummary(polarity_mean=0.0, polarity_std=0.0, n_items=0)

    mean = sum(vals) / len(vals)
    var = sum((v - mean) ** 2 for v in vals) / len(vals)
    return SentimentSummary(polarity_mean=float(mean), polarity_std=float(var**0.5), n_items=len(vals))


def get_sentiment_score() -> float:
    """
    Get overall sentiment score for market analysis.
    Returns sentiment in range [-1, 1].
    """
    items = fetch_google_news_rss("Nifty OR Indian stock market", limit=20)

    RISK_KEYWORDS = ["crash", "war", "panic", "default", "collapse", "recession"]
    POSITIVE_CONTEXT = ["resolved", "ends", "eases", "falls", "declines", "cooling", "recovery"]
    risk_hits = 0

    for item in items:
        title = (item.title or "").lower()

        if any(word in title for word in RISK_KEYWORDS):
            if not any(pos in title for pos in POSITIVE_CONTEXT):
                risk_hits += 1

    if risk_hits >= 2:
        return -0.8

    summary = summarize_news_sentiment(items)

    if summary.n_items < 5:
        return 0

    # Penalize high disagreement in news
    adjusted_score = summary.polarity_mean

    if summary.polarity_std > 0.4:
        adjusted_score *= 0.5  # reduce confidence

    return adjusted_score
