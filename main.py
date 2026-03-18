#!/usr/bin/env python3
"""
CLI interface for the Nifty Risk Engine.
"""

from nifty_risk_bot.core.engine import run_engine


def main():
    """Run the risk analysis and print results to terminal."""
    result, _ = run_engine()

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