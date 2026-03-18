from __future__ import annotations

from dataclasses import dataclass

from textblob import TextBlob

from data_fetcher import NewsItem, fetch_google_news_rss


@dataclass(frozen=True)
class SentimentSummary:
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
    if not items:
        return SentimentSummary(polarity_mean=0.0, polarity_std=0.0, n_items=0)

    vals = [headline_sentiment(i.title) for i in items if (i.title or "").strip()]
    if not vals:
        return SentimentSummary(polarity_mean=0.0, polarity_std=0.0, n_items=0)

    mean = sum(vals) / len(vals)
    var = sum((v - mean) ** 2 for v in vals) / len(vals)
    return SentimentSummary(polarity_mean=float(mean), polarity_std=float(var**0.5), n_items=len(vals))


def get_sentiment_score():
    items = fetch_google_news_rss("Nifty OR Indian stock market", limit=20)
    summary = summarize_news_sentiment(items)

    if summary.n_items < 5:
        return 0

    # Penalize high disagreement in news
    adjusted_score = summary.polarity_mean

    if summary.polarity_std > 0.4:
        adjusted_score *= 0.5  # reduce confidence

    return adjusted_score
