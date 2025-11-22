#!/usr/bin/env python3
"""
Test API Gateway endpoints
"""

import requests
import json

# Local testing
BASE_URL = "http://localhost:5001/api"

# AWS API Gateway URL (replace after deployment)
# BASE_URL = "https://your-api-id.execute-api.us-east-1.amazonaws.com/Prod"

def test_endpoints():
    print("🧪 Testing Trading API Gateway...")
    
    # Test stock data
    print("\n📊 Testing stock data endpoint:")
    try:
        response = requests.get(f"{BASE_URL}/stock/AAPL")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ AAPL: ${data['price']:.2f} ({data['change_percent']:+.2f}%)")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    # Test AI analysis
    print("\n🤖 Testing AI analysis endpoint:")
    try:
        response = requests.get(f"{BASE_URL}/analysis/TSLA")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ TSLA Analysis: {data['analysis'][:100]}...")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    # Test trading signals
    print("\n🎯 Testing signals endpoint:")
    try:
        response = requests.get(f"{BASE_URL}/signals/MSFT")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ MSFT Signal: {data['signal']} (Confidence: {data['confidence']:.0%})")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    # Test portfolio
    print("\n💼 Testing portfolio endpoint:")
    try:
        response = requests.get(f"{BASE_URL}/portfolio")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Portfolio Value: ${data['total_value']:,.2f}")
            print(f"   Positions: {len(data['positions'])}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    # Test market overview
    print("\n🌍 Testing market overview:")
    try:
        response = requests.get(f"{BASE_URL}/market-overview")
        if response.status_code == 200:
            data = response.json()
            print("✅ Market Overview:")
            for symbol, info in data['overview'].items():
                print(f"   {symbol}: ${info['price']:.2f} ({info['change_percent']:+.2f}%)")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    # Test screener
    print("\n🔍 Testing screener endpoint:")
    try:
        criteria = {
            "symbols": ["AAPL", "MSFT", "GOOGL"],
            "min_price": 100,
            "max_price": 500
        }
        response = requests.post(f"{BASE_URL}/screener", json=criteria)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Screener found {data['count']} stocks")
            for stock in data['results']:
                print(f"   {stock['symbol']}: ${stock['price']:.2f}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    # Test health check
    print("\n❤️ Testing health endpoint:")
    try:
        response = requests.get(f"{BASE_URL.replace('/api', '')}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data['status']}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    test_endpoints()