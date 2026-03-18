# nifty-risk-bot

Simple, modular Python project for market risk analysis:

- `data_fetcher.py`: price history + RSS headlines
- `sentiment.py`: headline sentiment scoring
- `scoring_engine.py`: risk metrics + 0–100 risk score
- `main.py`: CLI runner
- `app.py`: Streamlit dashboard

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run (CLI)

```bash
python main.py --symbol ^NSEI
```

## Run (Dashboard)

```bash
streamlit run app.py
```

## Notes

- Price data uses Yahoo Finance via `yfinance`.
- Headlines use Google News RSS (no API key). Availability can vary.

