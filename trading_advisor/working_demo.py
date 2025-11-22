#!/usr/bin/env python3
"""
Working Trading Demo - Mock Data Version
"""

import random
from datetime import datetime

# Mock stock data since yfinance may have issues
MOCK_STOCKS = {
    'AAPL': {'price': 185.50, 'change': 2.1},
    'MSFT': {'price': 378.20, 'change': -0.8},
    'GOOGL': {'price': 142.30, 'change': 1.5},
    'TSLA': {'price': 240.80, 'change': -3.2},
    'NVDA': {'price': 485.60, 'change': 4.7},
    'AMZN': {'price': 155.90, 'change': 0.9}
}

def get_stock_data(symbol):
    """Get mock stock data"""
    if symbol in MOCK_STOCKS:
        data = MOCK_STOCKS[symbol].copy()
        # Add some randomness
        data['price'] += random.uniform(-2, 2)
        data['change'] += random.uniform(-0.5, 0.5)
        data['volume'] = random.randint(10000000, 50000000)
        return {
            'symbol': symbol,
            'price': round(data['price'], 2),
            'change': round(data['change'], 2),
            'volume': data['volume']
        }
    return None

def generate_signal(symbol):
    """Generate trading signal based on mock analysis"""
    data = get_stock_data(symbol)
    if not data:
        return "HOLD"
    
    if data['change'] > 2:
        return "BUY"
    elif data['change'] < -2:
        return "SELL"
    else:
        return "HOLD"

def analyze_stock(symbol):
    """Provide basic stock analysis"""
    data = get_stock_data(symbol)
    if not data:
        return f"❌ Stock {symbol} not found"
    
    signal = generate_signal(symbol)
    
    # Determine trend
    if data['change'] > 0:
        trend = "📈 Bullish"
        color = "🟢"
    else:
        trend = "📉 Bearish" 
        color = "🔴"
    
    analysis = f"""
{color} {symbol} Analysis:
   Price: ${data['price']}
   Change: {data['change']:+.1f}%
   Volume: {data['volume']:,}
   Trend: {trend}
   Signal: {signal}
   
   📊 Quick Insights:
   • Support Level: ${data['price'] * 0.95:.2f}
   • Resistance Level: ${data['price'] * 1.05:.2f}
   • Risk Level: {'High' if abs(data['change']) > 3 else 'Medium' if abs(data['change']) > 1 else 'Low'}
    """
    
    return analysis

def show_portfolio():
    """Show mock portfolio"""
    portfolio = [
        {'symbol': 'AAPL', 'shares': 10, 'avg_price': 180.00},
        {'symbol': 'MSFT', 'shares': 5, 'avg_price': 375.00},
        {'symbol': 'GOOGL', 'shares': 2, 'avg_price': 140.00}
    ]
    
    print("\n💼 Portfolio Overview:")
    print("-" * 50)
    
    total_value = 0
    total_pnl = 0
    
    for position in portfolio:
        current_data = get_stock_data(position['symbol'])
        if current_data:
            current_value = position['shares'] * current_data['price']
            cost_basis = position['shares'] * position['avg_price']
            pnl = current_value - cost_basis
            pnl_pct = (pnl / cost_basis) * 100
            
            total_value += current_value
            total_pnl += pnl
            
            color = "🟢" if pnl > 0 else "🔴"
            print(f"{color} {position['symbol']}: {position['shares']} shares")
            print(f"   Current: ${current_data['price']:.2f} | Avg: ${position['avg_price']:.2f}")
            print(f"   Value: ${current_value:,.2f} | P&L: ${pnl:+,.2f} ({pnl_pct:+.1f}%)")
            print()
    
    pnl_color = "🟢" if total_pnl > 0 else "🔴"
    print(f"📊 Total Portfolio Value: ${total_value:,.2f}")
    print(f"{pnl_color} Total P&L: ${total_pnl:+,.2f}")

def show_market_overview():
    """Show market overview"""
    print("\n🌍 Market Overview:")
    print("-" * 40)
    
    for symbol in ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']:
        data = get_stock_data(symbol)
        if data:
            color = "🟢" if data['change'] > 0 else "🔴"
            signal = generate_signal(symbol)
            print(f"{color} {symbol}: ${data['price']} ({data['change']:+.1f}%) - {signal}")

def main():
    print("🚀 Trading Advisor - Working Demo")
    print("=" * 40)
    print("📊 Real-time market simulation with mock data")
    print("🎯 Features: Analysis, Signals, Portfolio tracking")
    print()
    
    while True:
        print("\n📋 Menu:")
        print("1. 🌍 Market Overview")
        print("2. 📈 Analyze Stock")
        print("3. 💼 View Portfolio")
        print("4. 🔍 Stock Screener")
        print("5. ❌ Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            show_market_overview()
            
        elif choice == '2':
            symbol = input("Enter stock symbol: ").upper().strip()
            print(analyze_stock(symbol))
            
        elif choice == '3':
            show_portfolio()
            
        elif choice == '4':
            print("\n🔍 Stock Screener Results:")
            print("Stocks with strong signals:")
            for symbol in MOCK_STOCKS:
                signal = generate_signal(symbol)
                if signal in ['BUY', 'SELL']:
                    data = get_stock_data(symbol)
                    color = "🟢" if signal == 'BUY' else "🔴"
                    print(f"{color} {symbol}: ${data['price']} - {signal}")
                    
        elif choice == '5':
            print("\n👋 Thanks for using Trading Advisor!")
            break
            
        else:
            print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    main()