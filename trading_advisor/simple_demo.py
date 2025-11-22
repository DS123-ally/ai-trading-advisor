#!/usr/bin/env python3
"""
Simple Trading Demo - Minimal Dependencies
"""

import yfinance as yf
import pandas as pd
from datetime import datetime

def get_stock_data(symbol):
    """Get basic stock data"""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="5d")
        
        if hist.empty:
            return None
            
        current_price = hist['Close'].iloc[-1]
        prev_price = hist['Close'].iloc[0]
        change_pct = ((current_price - prev_price) / prev_price) * 100
        
        return {
            'symbol': symbol,
            'price': round(current_price, 2),
            'change': round(change_pct, 2),
            'volume': int(hist['Volume'].iloc[-1])
        }
    except:
        return None

def generate_signal(symbol):
    """Generate simple trading signal"""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="30d")
        
        # Simple moving average
        sma_10 = hist['Close'].rolling(10).mean().iloc[-1]
        current_price = hist['Close'].iloc[-1]
        
        if current_price > sma_10:
            return "BUY"
        elif current_price < sma_10:
            return "SELL"
        else:
            return "HOLD"
    except:
        return "HOLD"

def main():
    print("🚀 Trading Advisor Demo")
    print("=" * 30)
    
    # Watchlist
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA']
    
    print("\n📊 Market Overview:")
    for symbol in symbols:
        data = get_stock_data(symbol)
        if data:
            signal = generate_signal(symbol)
            color = "🟢" if data['change'] > 0 else "🔴"
            print(f"{color} {symbol}: ${data['price']} ({data['change']:+.1f}%) - Signal: {signal}")
    
    print("\n🎯 Interactive Mode:")
    while True:
        symbol = input("\nEnter stock symbol (or 'quit'): ").upper()
        
        if symbol == 'QUIT':
            break
            
        data = get_stock_data(symbol)
        if data:
            signal = generate_signal(symbol)
            print(f"\n📈 {symbol} Analysis:")
            print(f"   Price: ${data['price']}")
            print(f"   Change: {data['change']:+.1f}%")
            print(f"   Volume: {data['volume']:,}")
            print(f"   Signal: {signal}")
        else:
            print(f"❌ Could not fetch data for {symbol}")
    
    print("\n👋 Thanks for using Trading Advisor!")

if __name__ == "__main__":
    main()