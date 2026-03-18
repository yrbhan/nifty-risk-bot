"""
Data fetching and models for the Nifty Risk Engine.
"""

from .fetcher import fetch_market_snapshot, fetch_gift_nifty_data
from .models import NewsItem

__all__ = ["fetch_market_snapshot", "fetch_gift_nifty_data", "NewsItem"]
