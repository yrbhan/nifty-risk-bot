from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import feedparser
import pandas as pd
import yfinance as yf


@dataclass(frozen=True)
class NewsItem:
    title: str
    published_at: Optional[datetime]
    link: Optional[str] = None
    source: str = "rss"


def fetch_price_history(
    symbol: str,
    period: str = "6mo",
    interval: str = "1d",
) -> pd.DataFrame:
    """
    Returns OHLCV history as a DataFrame indexed by timestamp.
    Uses Yahoo Finance via yfinance for simplicity.
    """
    df = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=False)
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    df.index = pd.to_datetime(df.index)
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    return df


def fetch_google_news_rss(query: str, limit: int = 25) -> list[NewsItem]:
    """
    Fetches headlines via Google News RSS. No API key required.
    Note: RSS availability can vary by region/time.
    """
    q = query.strip().replace(" ", "+")
    url = f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(url)

    items: list[NewsItem] = []
    for entry in (feed.entries or [])[: max(0, limit)]:
        published_at = None
        try:
            if getattr(entry, "published_parsed", None):
                published_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        except Exception:
            published_at = None

        items.append(
            NewsItem(
                title=str(getattr(entry, "title", "")).strip(),
                published_at=published_at,
                link=str(getattr(entry, "link", "")).strip() or None,
                source="google_news_rss",
            )
        )

    return items


def fetch_market_snapshot() -> dict[str, float | None]:
    """
    Fetches a small set of market risk inputs using yfinance.

    Returns keys:
    - vix_today
    - vix_3day_avg
    - sp500_1d_return
    - nasdaq_1d_return
    - nifty_3d_return
    """
    symbols = {
        "vix": "^INDIAVIX",
        "nifty": "^NSEI",
        "sp500": "^GSPC",
        "nasdaq": "^IXIC",
    }

    def last_close(sym: str) -> pd.Series:
        df = yf.download(sym, period="10d", interval="1d", progress=False, auto_adjust=False)
        if df is None or df.empty:
            return pd.Series(dtype=float)
        s = df["Close"].dropna().astype(float)
        s.index = pd.to_datetime(s.index)
        return s

    vix_close = last_close(symbols["vix"])
    sp_close = last_close(symbols["sp500"])
    nas_close = last_close(symbols["nasdaq"])
    nifty_close = last_close(symbols["nifty"])

    def one_day_return(close: pd.Series) -> float | None:
        if close.size < 2:
            return None
        return float(((close.iloc[-1].item() / close.iloc[-2].item()) - 1.0) * 100)


    def three_day_return(close: pd.Series) -> float | None:
        if close.size < 4:
            return None
        return float(((close.iloc[-1].item() / close.iloc[-4].item()) - 1.0) * 100)

    vix_today = None if vix_close.size < 1 else float(vix_close.iloc[-1].item())
    vix_3day_avg = None if vix_close.size < 3 else float(vix_close.iloc[-3:].mean().item())

    return {
        "vix_today": vix_today or 0,
        "vix_3day_avg": vix_3day_avg or 0,
        "sp500_1d_return": one_day_return(sp_close) or 0,
        "nasdaq_1d_return": one_day_return(nas_close) or 0,
        "nifty_1d_return": one_day_return(nifty_close) or 0,
        "nifty_3d_return": three_day_return(nifty_close) or 0,
    }

