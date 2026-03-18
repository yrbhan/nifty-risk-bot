"""
Data models for the Nifty Risk Engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class NewsItem:
    """Represents a news article with metadata."""
    title: str
    published_at: Optional[datetime]
    link: Optional[str] = None
    source: str = "rss"
