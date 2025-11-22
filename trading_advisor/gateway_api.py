#!/usr/bin/env python3
"""
Trading System with API Gateway Integration
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf
import boto3
import json
import requests
from datetime import datetime
import pandas as pd

app = Flask(__name__)
CORS(app)

# Initialize AWS services
try:
    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
    api_gateway = boto3.client('apigateway', region_name='us-east-1')
except:
    bedrock = None
    api_gateway = None

# API Gateway endpoints
@app.route('/api/stock/<symbol>', methods=['GET'])
def get_stock_data(symbol):
    """Get stock data via API Gateway"""
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
        
        return jsonify({
            'symbol': symbol,
            'price': float(current_price),
            'change': float(change),
            'change_percent': float(change_pct),
            'volume': int(hist['Volume'].iloc[-1]),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis/<symbol>', methods=['GET'])
def get_ai_analysis(symbol):
    """Get AI analysis via API Gateway"""
    if not bedrock:
        return jsonify({'error': 'Bedrock unavailable'}), 503
    
    try:
        # Get stock data for context
        stock = yf.Ticker(symbol)
        hist = stock.history(period="30d")
        current_price = hist['Close'].iloc[-1]
        
        prompt = f"""
        Analyze {symbol} stock:
        Current Price: ${current_price:.2f}
        30-day performance trend
        
        Provide:
        1. Technical outlook
        2. Trading recommendation
        3. Key levels to watch
        """
        
        body = json.dumps({
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 200,
                "temperature": 0.3,
                "topP": 0.9
            }
        })
        
        response = bedrock.invoke_model(
            modelId='amazon.titan-text-express-v1',
            body=body,
            contentType='application/json'
        )
        
        result = json.loads(response['body'].read())
        analysis = result['results'][0]['outputText'].strip()
        
        return jsonify({
            'symbol': symbol,
            'analysis': analysis,
            'price': float(current_price),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/signals/<symbol>', methods=['GET'])
def get_trading_signals(symbol):
    """Get trading signals via API Gateway"""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="60d")
        
        # Calculate indicators
        hist['SMA_20'] = hist['Close'].rolling(20).mean()
        hist['SMA_50'] = hist['Close'].rolling(50).mean()
        
        current_price = hist['Close'].iloc[-1]
        sma_20 = hist['SMA_20'].iloc[-1]
        sma_50 = hist['SMA_50'].iloc[-1]
        
        # Generate signal
        if current_price > sma_20 > sma_50:
            signal = "BUY"
            confidence = 0.8
        elif current_price < sma_20 < sma_50:
            signal = "SELL"
            confidence = 0.7
        else:
            signal = "HOLD"
            confidence = 0.5
        
        return jsonify({
            'symbol': symbol,
            'signal': signal,
            'confidence': confidence,
            'price': float(current_price),
            'sma_20': float(sma_20),
            'sma_50': float(sma_50),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    """Get portfolio data via API Gateway"""
    # Mock portfolio data
    positions = [
        {'symbol': 'AAPL', 'quantity': 10, 'avg_price': 150.00},
        {'symbol': 'MSFT', 'quantity': 5, 'avg_price': 300.00},
        {'symbol': 'GOOGL', 'quantity': 2, 'avg_price': 2500.00}
    ]
    
    total_value = 0
    
    for position in positions:
        try:
            stock = yf.Ticker(position['symbol'])
            hist = stock.history(period="1d")
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
        'positions': positions,
        'total_value': total_value,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/market-overview', methods=['GET'])
def get_market_overview():
    """Get market overview via API Gateway"""
    symbols = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'GOOGL', 'TSLA']
    overview = {}
    
    for symbol in symbols:
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1d")
            current_price = hist['Close'].iloc[-1]
            change_pct = ((current_price - hist['Open'].iloc[0]) / hist['Open'].iloc[0]) * 100
            
            overview[symbol] = {
                'price': float(current_price),
                'change_percent': float(change_pct)
            }
        except:
            continue
    
    return jsonify({
        'overview': overview,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/screener', methods=['POST'])
def stock_screener():
    """Stock screener via API Gateway"""
    criteria = request.json
    symbols = criteria.get('symbols', ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA'])
    min_price = criteria.get('min_price', 0)
    max_price = criteria.get('max_price', 10000)
    
    results = []
    
    for symbol in symbols:
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1d")
            price = hist['Close'].iloc[-1]
            
            if min_price <= price <= max_price:
                results.append({
                    'symbol': symbol,
                    'price': float(price),
                    'volume': int(hist['Volume'].iloc[-1])
                })
        except:
            continue
    
    return jsonify({
        'results': results,
        'count': len(results),
        'criteria': criteria,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'services': {
            'bedrock': 'available' if bedrock else 'unavailable',
            'api_gateway': 'available' if api_gateway else 'unavailable'
        },
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🌐 Starting Trading API Gateway...")
    print("📊 Available endpoints:")
    print("  GET  /api/stock/<symbol>")
    print("  GET  /api/analysis/<symbol>")
    print("  GET  /api/signals/<symbol>")
    print("  GET  /api/portfolio")
    print("  GET  /api/market-overview")
    print("  POST /api/screener")
    print("  GET  /health")
    print("\n🚀 Server running at: http://localhost:5001")
    
    app.run(debug=True, host='0.0.0.0', port=5001)