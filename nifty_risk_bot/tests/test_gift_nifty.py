#!/usr/bin/env python3
"""
Test script to verify GIFT NIFTY integration
"""

from ...data.fetcher import fetch_market_snapshot, fetch_gift_nifty_data
from ...core.scoring import calculate_score


def test_gift_nifty_integration():
    print("=== Testing GIFT NIFTY Integration ===\n")
    
    # Test 1: Fetch market snapshot (includes GIFT NIFTY)
    print("1. Testing market snapshot with GIFT NIFTY...")
    market_data = fetch_market_snapshot()
    
    print(f"   GIFT NIFTY Current: {market_data.get('gift_nifty_current')}")
    print(f"   GIFT NIFTY Change %: {market_data.get('gift_nifty_change_pct')}")
    print(f"   GIFT NIFTY Close Value: {market_data.get('gift_nifty_close_value')}")
    print()
    
    # Test 2: Test scoring with simulated GIFT NIFTY data
    print("2. Testing scoring with simulated GIFT NIFTY movements...")
    
    # Simulate different scenarios
    test_scenarios = [
        {"gift_nifty_change_pct": -2.0, "description": "Large gap down"},
        {"gift_nifty_change_pct": -1.0, "description": "Moderate gap down"},
        {"gift_nifty_change_pct": -0.5, "description": "Mild gap down"},
        {"gift_nifty_change_pct": 0.2, "description": "Small gap up"},
        {"gift_nifty_change_pct": 1.5, "description": "Large gap up"},
    ]
    
    base_data = {
        "vix_today": 15.0,
        "vix_3day_avg": 16.0,
        "sp500_1d_return": 0.5,
        "nasdaq_1d_return": 0.8,
        "nifty_1d_return": 0.3,
        "nifty_3d_return": 0.8,
    }
    
    for scenario in test_scenarios:
        test_data = base_data.copy()
        test_data["gift_nifty_change_pct"] = scenario["gift_nifty_change_pct"]
        
        result = calculate_score(test_data)
        
        print(f"   {scenario['description']} ({scenario['gift_nifty_change_pct']:+.1f}%):")
        print(f"     Score: {result['score']}/100")
        print(f"     Risk: {result['risk']}")
        print(f"     Direction: {result['direction']} {result['strength']}")
        print(f"     Key reasons: {[r for r in result['reasons'] if 'pre-market' in r.lower() or 'gap' in r.lower()]}")
        print()


if __name__ == "__main__":
    test_gift_nifty_integration()
