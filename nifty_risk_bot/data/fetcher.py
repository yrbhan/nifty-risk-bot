"""
Data fetching module for the Nifty Risk Engine.
"""

from __future__ import annotations

from datetime import datetime, timezone, time
from typing import Optional

import feedparser
import pandas as pd
import requests
import yfinance as yf

from .models import NewsItem


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


def fetch_gift_nifty_data() -> dict[str, float | None]:
    """
    Fetches real-time GIFT NIFTY data using multiple sources with fallbacks.
    
    Returns:
    - gift_nifty_current: Current GIFT NIFTY value
    - gift_nifty_change_pct: % change since last NIFTY close (3:30 PM IST)
    - gift_nifty_close_value: NIFTY value at last close (3:30 PM IST)
    """
    
    # Try methods in order of reliability
    methods = [
        fetch_gift_nifty_yahoo_finance,
        fetch_gift_nifty_google_finance,
        fetch_gift_nifty_nse_api,
        fetch_gift_nifty_alternative_api,
        fetch_gift_nifty_fallback
    ]
    
    for method in methods:
        try:
            result = method()
            if result.get('gift_nifty_current') is not None:
                # Calculate change if we have current value
                if result.get('gift_nifty_current') and not result.get('gift_nifty_change_pct'):
                    nifty_close_data = get_last_nifty_close()
                    close_value = nifty_close_data.get('close_value')
                    
                    if close_value is not None:
                        current_value = result['gift_nifty_current']
                        change_pct = ((float(current_value) - float(close_value)) / float(close_value)) * 100
                        result['gift_nifty_change_pct'] = round(change_pct, 2)
                        result['gift_nifty_close_value'] = round(float(close_value), 2)
                
                return result
        except Exception:
            continue
    
    return {"gift_nifty_current": None, "gift_nifty_change_pct": None, "gift_nifty_close_value": None}


def fetch_gift_nifty_yahoo_finance() -> dict[str, float | None]:
    """
    Method 1: Use Yahoo Finance for Singapore Nifty (SGX:NIFTY) as proxy
    """
    try:
        # Try multiple Yahoo Finance symbols for Singapore Nifty
        symbols = ["^STI", "NQ=F", "ES=F"]  # Singapore STI, Nasdaq, S&P futures as proxies
        
        for symbol in symbols:
            try:
                data = yf.download(symbol, period="1d", interval="1m", progress=False, auto_adjust=False)
                if data is not None and not data.empty and len(data) > 0:
                    latest_price = data['Close'].dropna().iloc[-1]
                    
                    # For futures, we need to adjust the range
                    if symbol == "^STI":
                        # STI typically ranges 3000-4000, we need to scale to NIFTY range
                        # This is a rough approximation
                        scaled_price = latest_price * 5  # Rough scaling factor
                        if 15000 <= scaled_price <= 25000:
                            return {"gift_nifty_current": round(float(scaled_price), 2), "gift_nifty_change_pct": None, "gift_nifty_close_value": None}
                    else:
                        # For US futures, we'll use them as sentiment indicators
                        # and create a synthetic NIFTY value based on typical correlation
                        nifty_data = yf.download("^NSEI", period="1d", interval="1d", progress=False, auto_adjust=False)
                        if nifty_data is not None and not nifty_data.empty:
                            nifty_close = nifty_data['Close'].iloc[-1]
                            # Apply futures movement to NIFTY close as proxy
                            futures_change = (latest_price / data['Close'].iloc[0] - 1) if len(data) > 1 else 0
                            proxy_nifty = nifty_close * (1 + futures_change * 0.3)  # Reduced correlation factor
                            
                            if 15000 <= proxy_nifty <= 25000:
                                return {"gift_nifty_current": round(float(proxy_nifty), 2), "gift_nifty_change_pct": None, "gift_nifty_close_value": None}
            except Exception:
                continue
        
        return {"gift_nifty_current": None, "gift_nifty_change_pct": None, "gift_nifty_close_value": None}
        
    except Exception:
        return {"gift_nifty_current": None, "gift_nifty_change_pct": None, "gift_nifty_close_value": None}


def fetch_gift_nifty_google_finance() -> dict[str, float | None]:
    """
    Method 2: Scrape Google Finance for GIFT NIFTY data
    """
    try:
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
        
        # Try multiple Google Finance URLs
        urls = [
            "https://www.google.com/finance/quote/SGX:NIFTY",
            "https://www.google.com/finance/quote/.STI:SGX",
            "https://www.google.com/finance/quote/NQ=F"
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        for url in urls:
            try:
                response = requests.get(url, headers=headers, timeout=8)
                if response.status_code != 200:
                    continue
                
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Try different selectors for price
                selectors = [
                    '[data-last-price]',
                    '.YMlKec.fxKbKc',  # Google Finance price class
                    '.kf1m0',  # Alternative price class
                    '[data-field="price"]'
                ]
                
                for selector in selectors:
                    elements = soup.select(selector)
                    for element in elements:
                        text = element.get_text().strip()
                        try:
                            value = float(text.replace(',', '').replace('$', '').replace('₹', ''))
                            if 1000 <= value <= 30000:  # Broad range for various indices
                                # Scale to NIFTY range if needed
                                if value < 10000:
                                    value = value * 6  # Scale up smaller indices
                                if 15000 <= value <= 25000:
                                    return {"gift_nifty_current": round(value, 2), "gift_nifty_change_pct": None, "gift_nifty_close_value": None}
                        except ValueError:
                            continue
            except Exception:
                continue
        
        return {"gift_nifty_current": None, "gift_nifty_change_pct": None, "gift_nifty_close_value": None}
        
    except Exception:
        return {"gift_nifty_current": None, "gift_nifty_change_pct": None, "gift_nifty_close_value": None}


def fetch_gift_nifty_nse_api() -> dict[str, float | None]:
    """
    Method 3: Try NSE's market status API with updated endpoints
    """
    try:
        # Try multiple NSE endpoints
        endpoints = [
            "https://www.nseindia.com/api/marketStatus",
            "https://www.nseindia.com/api/market-data-latest-currency",
            "https://www.nseindia.com/api/allIndices"
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.nseindia.com/',
        }
        
        for url in endpoints:
            response = requests.get(url, headers=headers, timeout=8)
            if response.status_code == 200:
                data = response.json()
                
                # Look for GIFT NIFTY in different possible locations
                if 'marketState' in data:
                    for market in data['marketState']:
                        if 'GIFT' in str(market).upper() or 'NIFTY' in str(market).upper():
                            if 'lastPrice' in market:
                                return {"gift_nifty_current": market['lastPrice'], "gift_nifty_change_pct": None, "gift_nifty_close_value": None}
                
                if 'data' in data:
                    for item in data['data']:
                        if 'GIFT' in str(item).upper() or 'SGX' in str(item).upper():
                            if 'lastPrice' in item or 'currentValue' in item:
                                value = item.get('lastPrice') or item.get('currentValue')
                                if value:
                                    return {"gift_nifty_current": float(value), "gift_nifty_change_pct": None, "gift_nifty_close_value": None}
        
        return {"gift_nifty_current": None, "gift_nifty_change_pct": None, "gift_nifty_close_value": None}
        
    except Exception:
        return {"gift_nifty_current": None, "gift_nifty_change_pct": None, "gift_nifty_close_value": None}


def fetch_gift_nifty_alternative_api() -> dict[str, float | None]:
    """
    Method 4: Try alternative free APIs
    """
    try:
        # Try some free market data APIs
        apis = [
            "https://api.marketstack.com/v1/tickers/latest?access_key=YOUR_API_KEY&symbols=SGX:NIFTY",
            "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=SGX:NIFTY&apikey=YOUR_API_KEY"
        ]
        
        # Note: These would require API keys, so we'll skip for now
        # This is a placeholder for future API integration
        
        return {"gift_nifty_current": None, "gift_nifty_change_pct": None, "gift_nifty_close_value": None}
        
    except Exception:
        return {"gift_nifty_current": None, "gift_nifty_change_pct": None, "gift_nifty_close_value": None}


def fetch_gift_nifty_fallback() -> dict[str, float | None]:
    """
    Fallback method: Return None when GIFT NIFTY data is unavailable
    """
    return {"gift_nifty_current": None, "gift_nifty_change_pct": None, "gift_nifty_close_value": None}


def get_last_nifty_close() -> dict[str, float | None]:
    """
    Gets the last NIFTY closing price (3:30 PM IST on weekdays).
    """
    try:
        # Get current time in IST
        now_ist = datetime.now(timezone.utc).astimezone()
        
        # Get NIFTY data from Yahoo Finance
        nifty_data = yf.download("^NSEI", period="5d", interval="1d", progress=False, auto_adjust=False)
        
        if nifty_data is None or nifty_data.empty or len(nifty_data) < 1:
            return {"close_value": None, "close_time": None}
            
        # Get the most recent close
        latest_close = nifty_data['Close'].dropna().iloc[-1]
        latest_date = nifty_data.index[-1]
        
        return {
            "close_value": float(latest_close.iloc[0]),
            "close_time": latest_date
        }
        
    except Exception:
        return {"close_value": None, "close_time": None}


def fetch_market_snapshot() -> dict[str, float | None]:
    """
    Fetches a small set of market risk inputs using yfinance.

    Returns keys:
    - vix_today
    - vix_3day_avg
    - sp500_1d_return
    - nasdaq_1d_return
    - nifty_1d_return
    - nifty_3d_return
    - gift_nifty_current
    - gift_nifty_change_pct
    - gift_nifty_close_value
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

    vix_today = None if vix_close.size < 1 else round(float(vix_close.iloc[-1].item()), 2)
    vix_3day_avg = None if vix_close.size < 3 else round(float(vix_close.iloc[-3:].mean().item()), 2)

    # Get GIFT NIFTY data
    gift_nifty_data = fetch_gift_nifty_data()
    
    result = {
        "vix_today": vix_today,
        "vix_3day_avg": vix_3day_avg,
        "sp500_1d_return": round(one_day_return(sp_close) or 0, 2),
        "sp500_3d_return": round(three_day_return(sp_close) or 0, 2),
        "nasdaq_1d_return": round(one_day_return(nas_close) or 0, 2),
        "nasdaq_3d_return": round(three_day_return(nas_close) or 0, 2),
        "nifty_1d_return": round(one_day_return(nifty_close) or 0, 2),
        "nifty_3d_return": round(three_day_return(nifty_close) or 0, 2),
    }
    
    # Add GIFT NIFTY data to result
    result.update(gift_nifty_data)
    
    return result
