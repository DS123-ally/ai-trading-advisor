#!/usr/bin/env python3
"""
Enhanced Trading Backend - Standalone Flask API
Run: python3 enhanced_backend.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import sqlite3
import json
from datetime import datetime, timedelta
import threading
import time

app = Flask(__name__)
CORS(app)

# In-memory cache
cache = {}
cache_expiry = {}

class TradingDB:
    def __init__(self):
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect('trading.db')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY,
                symbol TEXT,
                signal TEXT,
                confidence REAL,
                price REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY,
                symbol TEXT,
                message TEXT,
                alert_type TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def save_signal(self, symbol, signal, confidence, price):
        conn = sqlite3.connect('trading.db')
        conn.execute(
            'INSERT INTO signals (symbol, signal, confidence, price) VALUES (?, ?, ?, ?)',
            (symbol, signal, confidence, price)
        )
        conn.commit()
        conn.close()
    
    def get_recent_signals(self, limit=10):
        conn = sqlite3.connect('trading.db')
        cursor = conn.execute(
            'SELECT * FROM signals ORDER BY timestamp DESC LIMIT ?',
            (limit,)
        )
        results = cursor.fetchall()
        conn.close()
        return results

db = TradingDB()

def get_cached_data(key, expiry_minutes=5):
    if key in cache and key in cache_expiry:
        if datetime.now() < cache_expiry[key]:
            return cache[key]
    return None

def set_cache(key, data, expiry_minutes=5):
    cache[key] = data
    cache_expiry[key] = datetime.now() + timedelta(minutes=expiry_minutes)

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def generate_trading_signal(symbol):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="60d")
        
        if hist.empty:
            return None
        
        # Technical indicators
        hist['SMA_20'] = hist['Close'].rolling(20).mean()
        hist['SMA_50'] = hist['Close'].rolling(50).mean()
        hist['RSI'] = calculate_rsi(hist['Close'])
        
        current_price = hist['Close'].iloc[-1]
        sma_20 = hist['SMA_20'].iloc[-1]
        sma_50 = hist['SMA_50'].iloc[-1]
        rsi = hist['RSI'].iloc[-1]
        
        # Signal generation
        if current_price > sma_20 > sma_50 and rsi < 70:
            signal = "BUY"
            confidence = 0.8
        elif current_price < sma_20 < sma_50 and rsi > 30:
            signal = "SELL"
            confidence = 0.7
        else:
            signal = "HOLD"
            confidence = 0.5
        
        # Save to database
        db.save_signal(symbol, signal, confidence, float(current_price))
        
        return {
            'symbol': symbol,
            'signal': signal,
            'confidence': confidence,
            'price': float(current_price),
            'indicators': {
                'sma_20': float(sma_20),
                'sma_50': float(sma_50),
                'rsi': float(rsi)
            },
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {'error': str(e)}

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'cache_size': len(cache)
    })

@app.route('/api/stock/<symbol>')
def get_stock(symbol):
    # Check cache first
    cached = get_cached_data(f"stock_{symbol}")
    if cached:
        return jsonify(cached)
    
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1d")
        info = stock.info
        
        if hist.empty:
            return jsonify({'error': 'Stock not found'}), 404
        
        current_price = hist['Close'].iloc[-1]
        prev_close = info.get('previousClose', hist['Open'].iloc[0])
        change = current_price - prev_close
        change_pct = (change / prev_close) * 100
        
        data = {
            'symbol': symbol,
            'price': float(current_price),
            'change': float(change),
            'change_percent': float(change_pct),
            'volume': int(hist['Volume'].iloc[-1]),
            'market_cap': info.get('marketCap'),
            'pe_ratio': info.get('trailingPE'),
            'timestamp': datetime.now().isoformat()
        }
        
        # Cache the result
        set_cache(f"stock_{symbol}", data, 1)  # 1 minute cache
        
        return jsonify(data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/signals/<symbol>')
def get_signals(symbol):
    # Check cache
    cached = get_cached_data(f"signals_{symbol}")
    if cached:
        return jsonify(cached)
    
    signal_data = generate_trading_signal(symbol)
    if signal_data:
        set_cache(f"signals_{symbol}", signal_data, 5)  # 5 minute cache
        return jsonify(signal_data)
    else:
        return jsonify({'error': 'Unable to generate signals'}), 500

@app.route('/api/batch-signals', methods=['POST'])
def batch_signals():
    symbols = request.json.get('symbols', [])
    results = {}
    
    for symbol in symbols[:10]:  # Limit to 10 symbols
        signal_data = generate_trading_signal(symbol)
        if signal_data:
            results[symbol] = signal_data
    
    return jsonify(results)

@app.route('/api/market-overview')
def market_overview():
    cached = get_cached_data("market_overview")
    if cached:
        return jsonify(cached)
    
    # Major indices and popular stocks
    symbols = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
    overview = {}
    
    for symbol in symbols:
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1d")
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                change_pct = ((current_price - hist['Open'].iloc[0]) / hist['Open'].iloc[0]) * 100
                
                overview[symbol] = {
                    'price': float(current_price),
                    'change_percent': float(change_pct)
                }
        except:
            continue
    
    result = {
        'overview': overview,
        'timestamp': datetime.now().isoformat()
    }
    
    set_cache("market_overview", result, 2)  # 2 minute cache
    return jsonify(result)

@app.route('/api/screener', methods=['POST'])
def stock_screener():
    criteria = request.json
    symbols = criteria.get('symbols', ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'AMZN', 'META'])
    
    min_price = criteria.get('min_price', 0)
    max_price = criteria.get('max_price', 10000)
    min_volume = criteria.get('min_volume', 0)
    
    results = []
    
    for symbol in symbols:
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1d")
            
            if not hist.empty:
                price = hist['Close'].iloc[-1]
                volume = hist['Volume'].iloc[-1]
                
                if min_price <= price <= max_price and volume >= min_volume:
                    signal_data = generate_trading_signal(symbol)
                    if signal_data:
                        results.append({
                            'symbol': symbol,
                            'price': float(price),
                            'volume': int(volume),
                            'signal': signal_data['signal'],
                            'confidence': signal_data['confidence']
                        })
        except:
            continue
    
    return jsonify({
        'results': results,
        'count': len(results),
        'criteria': criteria,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/recent-signals')
def recent_signals():
    signals = db.get_recent_signals(20)
    
    formatted_signals = []
    for signal in signals:
        formatted_signals.append({
            'id': signal[0],
            'symbol': signal[1],
            'signal': signal[2],
            'confidence': signal[3],
            'price': signal[4],
            'timestamp': signal[5]
        })
    
    return jsonify({
        'signals': formatted_signals,
        'count': len(formatted_signals)
    })

@app.route('/api/portfolio/<user_id>')
def get_portfolio(user_id):
    # Mock portfolio data - replace with actual database
    mock_portfolio = {
        'demo_user': [
            {'symbol': 'AAPL', 'quantity': 10, 'avg_price': 150.00},
            {'symbol': 'MSFT', 'quantity': 5, 'avg_price': 300.00},
            {'symbol': 'GOOGL', 'quantity': 2, 'avg_price': 2500.00}
        ]
    }
    
    positions = mock_portfolio.get(user_id, [])
    total_value = 0
    
    for position in positions:
        try:
            stock = yf.Ticker(position['symbol'])
            hist = stock.history(period="1d")
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                position['current_price'] = float(current_price)
                position['market_value'] = position['quantity'] * current_price
                position['pnl'] = (current_price - position['avg_price']) * position['quantity']
                total_value += position['market_value']
        except:
            position['current_price'] = position['avg_price']
            position['market_value'] = position['quantity'] * position['avg_price']
            position['pnl'] = 0
    
    return jsonify({
        'user_id': user_id,
        'positions': positions,
        'total_value': total_value,
        'timestamp': datetime.now().isoformat()
    })

# Background task to clean old cache entries
def cleanup_cache():
    while True:
        time.sleep(300)  # Run every 5 minutes
        current_time = datetime.now()
        expired_keys = [key for key, expiry in cache_expiry.items() if current_time > expiry]
        
        for key in expired_keys:
            cache.pop(key, None)
            cache_expiry.pop(key, None)

# Start background cleanup thread
cleanup_thread = threading.Thread(target=cleanup_cache, daemon=True)
cleanup_thread.start()

if __name__ == '__main__':
    print("🚀 Starting Enhanced Trading Backend...")
    print("📊 API Endpoints:")
    print("  GET  /api/health")
    print("  GET  /api/stock/<symbol>")
    print("  GET  /api/signals/<symbol>")
    print("  POST /api/batch-signals")
    print("  GET  /api/market-overview")
    print("  POST /api/screener")
    print("  GET  /api/recent-signals")
    print("  GET  /api/portfolio/<user_id>")
    print("\n🌐 Server running at: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)