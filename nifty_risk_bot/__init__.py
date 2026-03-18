"""
Nifty Weekly Options Risk Engine

A modular Python-based decision system designed to evaluate market risk 
for weekly options selling strategies (theta decay).
"""

__version__ = "1.0.0"
__author__ = "Yash Bhan"

from .core.engine import run_engine
from .data.fetcher import fetch_market_snapshot
from .core.scoring import calculate_score
from .core.sentiment import get_sentiment_score

__all__ = [
    "run_engine",
    "fetch_market_snapshot", 
    "calculate_score",
    "get_sentiment_score"
]
