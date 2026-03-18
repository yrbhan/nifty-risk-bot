# 📊 Nifty Weekly Options Risk Engine

A modular Python-based decision system designed to evaluate **market risk for weekly options selling strategies** (theta decay).

This tool analyzes volatility, trend, global markets, and news sentiment to generate a **0–100 safety score** along with actionable trading guidance.

---

# 🎯 Purpose

This system is specifically built for:

* Weekly options sellers (e.g., short strangles, iron condors, spreads)
* Traders who want to **avoid high-risk market conditions**
* Structured, rule-based decision making instead of intuition

---

# 🧠 What the Score Means

| Score Range | Interpretation    | Suggested Approach                            |
| ----------- | ----------------- | --------------------------------------------- |
| 70 – 100    | 🟢 Low Risk       | Safe for option selling (range-bound markets) |
| 50 – 69     | 🟡 Moderate Risk  | Trade with hedges / reduced size              |
| 30 – 49     | 🔴 High Risk      | Directional trades only                       |
| 0 – 29      | 🚫 Very High Risk | Avoid trading                                 |

👉 **Higher score = safer for option selling**

---

# ⚠️ What “Risk” Refers To

This is **NOT general market risk**.

It specifically measures:

> **Risk of large directional or volatile moves that can cause losses in short option strategies**

---

# ⚙️ System Architecture

```text
data_fetcher → sentiment → scoring_engine → engine_runner → app / main
```

---

# 📦 Project Structure

## 1️⃣ `data_fetcher.py`

Responsible for fetching all raw inputs.

### Features:

* Fetches market data using `yfinance`
* Retrieves:

  * India VIX
  * Nifty index
  * S&P 500
  * Nasdaq
* Calculates:

  * 1-day returns
  * 3-day returns
* Fetches news headlines via Google News RSS

### Key Functions:

* `fetch_market_snapshot()` → returns all market indicators
* `fetch_google_news_rss()` → returns list of news headlines

---

## 2️⃣ `sentiment.py`

Processes news headlines to extract market sentiment.

### Features:

* Uses TextBlob for polarity scoring
* Computes:

  * Mean sentiment
  * Standard deviation (uncertainty)
* Filters low-confidence data
* Detects **risk keywords** (e.g., crash, war, panic)

### Key Function:

* `get_sentiment_score()` → returns value in range [-1, +1]

---

## 3️⃣ `scoring_engine.py`

Core decision engine of the system.

### Inputs:

* Market data
* Sentiment score
* Event risk flag

### Logic:

Evaluates:

* VIX trend (volatility)
* Nifty trend (directional movement)
* Global markets (US indices)
* News sentiment
* Recent shocks (large 1-day moves)

### Outputs:

* `score` (0–100)
* `risk` (Low / Moderate / High / Very High)
* `direction` (Bullish / Bearish / Neutral)
* `strength` (Strong / Weak)
* `trade` (suggested strategy)
* `position_size`
* `warning`
* `reasons`

---

## 4️⃣ `engine_runner.py`

Orchestrator layer.

### Responsibilities:

* Calls:

  * `data_fetcher`
  * `sentiment`
  * `scoring_engine`
* Returns:

  * final result
  * raw market data

---

## 5️⃣ `app.py` (Streamlit Dashboard)

User-facing interface.

### Features:

* Displays:

  * Safety score
  * Risk level
  * Market direction
  * Suggested trade
  * Position sizing
  * Reasons behind decision
* Designed for **quick decision making**

---

## 6️⃣ `main.py` (CLI Mode)

Command-line version of the engine.

### Usage:

* Prints analysis to terminal
* Useful for debugging or automation

---

# 🚀 Setup Instructions

## 1. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate   # Mac/Linux
.venv\Scripts\activate      # Windows
```

---

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ How to Run

## Run CLI Version

```bash
python main.py
```

---

## Run Dashboard

```bash
streamlit run app.py
```

---

# 📊 Data Sources

* Market data: Yahoo Finance (`yfinance`)
* News: Google News RSS (no API key required)

---

# ⚠️ Limitations

* News sentiment is heuristic-based (not full NLP)
* Data depends on Yahoo Finance availability
* Designed for **decision support**, not automated trading
* Does not yet include strike selection or execution

---

# 🔮 Future Enhancements

* Strike selection engine (auto-select options)
* Event calendar integration (Fed, budget, earnings)
* Live broker integration (Zerodha API)
* Backtesting module
* Advanced sentiment models

---

# 🧠 Key Philosophy

> “Avoid bad trades rather than chasing good trades.”

This system focuses on:

* Risk avoidance
* Capital protection
* Consistency over aggression

---

# 📌 Disclaimer

This tool is for educational and decision-support purposes only.
It does not constitute financial advice.

---

# 👨‍💻 Author

Built as a modular trading intelligence system for systematic options selling.
