import json
import boto3
import yfinance as yf
from datetime import datetime

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

def lambda_handler(event, context):
    try:
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        path_params = event.get('pathParameters') or {}
        query_params = event.get('queryStringParameters') or {}
        body = event.get('body')
        
        if body:
            body = json.loads(body)
        
        # Route requests
        if path.startswith('/stock/'):
            return handle_stock_data(path_params.get('symbol'))
        elif path.startswith('/analysis/'):
            return handle_analysis(path_params.get('symbol'))
        elif path.startswith('/signals/'):
            return handle_signals(path_params.get('symbol'))
        elif path == '/portfolio':
            return handle_portfolio()
        elif path == '/market-overview':
            return handle_market_overview()
        elif path == '/screener':
            return handle_screener(body)
        elif path == '/health':
            return handle_health()
        else:
            return error_response(404, 'Endpoint not found')
            
    except Exception as e:
        return error_response(500, str(e))

def handle_stock_data(symbol):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1d")
        
        if hist.empty:
            return error_response(404, 'Stock not found')
        
        current_price = hist['Close'].iloc[-1]
        change_pct = ((current_price - hist['Open'].iloc[0]) / hist['Open'].iloc[0]) * 100
        
        return success_response({
            'symbol': symbol,
            'price': float(current_price),
            'change_percent': float(change_pct),
            'volume': int(hist['Volume'].iloc[-1]),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return error_response(500, str(e))

def handle_analysis(symbol):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="30d")
        current_price = hist['Close'].iloc[-1]
        
        prompt = f"Analyze {symbol} stock at ${current_price:.2f}. Provide brief trading outlook."
        
        body = json.dumps({
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 150,
                "temperature": 0.3
            }
        })
        
        response = bedrock.invoke_model(
            modelId='amazon.titan-text-express-v1',
            body=body,
            contentType='application/json'
        )
        
        result = json.loads(response['body'].read())
        analysis = result['results'][0]['outputText'].strip()
        
        return success_response({
            'symbol': symbol,
            'analysis': analysis,
            'price': float(current_price),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return error_response(500, str(e))

def handle_signals(symbol):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="60d")
        
        hist['SMA_20'] = hist['Close'].rolling(20).mean()
        current_price = hist['Close'].iloc[-1]
        sma_20 = hist['SMA_20'].iloc[-1]
        
        signal = "BUY" if current_price > sma_20 else "SELL"
        confidence = 0.7
        
        return success_response({
            'symbol': symbol,
            'signal': signal,
            'confidence': confidence,
            'price': float(current_price),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return error_response(500, str(e))

def handle_portfolio():
    positions = [
        {'symbol': 'AAPL', 'quantity': 10, 'avg_price': 150.00},
        {'symbol': 'MSFT', 'quantity': 5, 'avg_price': 300.00}
    ]
    
    total_value = 0
    for position in positions:
        try:
            stock = yf.Ticker(position['symbol'])
            hist = stock.history(period="1d")
            current_price = hist['Close'].iloc[-1]
            
            position['current_price'] = float(current_price)
            position['market_value'] = position['quantity'] * current_price
            total_value += position['market_value']
        except:
            position['current_price'] = position['avg_price']
            position['market_value'] = position['quantity'] * position['avg_price']
    
    return success_response({
        'positions': positions,
        'total_value': total_value,
        'timestamp': datetime.now().isoformat()
    })

def handle_market_overview():
    symbols = ['SPY', 'AAPL', 'MSFT', 'GOOGL']
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
    
    return success_response({
        'overview': overview,
        'timestamp': datetime.now().isoformat()
    })

def handle_screener(criteria):
    if not criteria:
        criteria = {}
    
    symbols = criteria.get('symbols', ['AAPL', 'MSFT', 'GOOGL'])
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
                    'price': float(price)
                })
        except:
            continue
    
    return success_response({
        'results': results,
        'count': len(results),
        'timestamp': datetime.now().isoformat()
    })

def handle_health():
    return success_response({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

def success_response(data):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(data)
    }

def error_response(status_code, message):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({'error': message})
    }