from engine_runner import run_engine


def main():
    # ---------------------------
    # 1. Run Engine to calculate score
    # ---------------------------
    result, _ = run_engine()

    # ---------------------------
    # 5. Print Output
    # ---------------------------
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