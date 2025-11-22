"""
API Endpoints Reference for Trading System
"""

API_ENDPOINTS = {
    "Alpha Vantage": {
        "base_url": "https://www.alphavantage.co/query",
        "endpoints": {
            "daily_prices": "function=TIME_SERIES_DAILY&symbol={symbol}&apikey={key}",
            "intraday": "function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={key}",
            "news_sentiment": "function=NEWS_SENTIMENT&tickers={symbol}&apikey={key}",
            "technical_indicators": "function=RSI&symbol={symbol}&interval=daily&time_period=14&series_type=close&apikey={key}",
            "earnings": "function=EARNINGS&symbol={symbol}&apikey={key}",
            "company_overview": "function=OVERVIEW&symbol={symbol}&apikey={key}"
        },
        "rate_limit": "5 calls per minute, 500 per day (free tier)"
    },
    
    "Polygon": {
        "base_url": "https://api.polygon.io",
        "endpoints": {
            "daily_bars": "/v2/aggs/ticker/{symbol}/range/1/day/{from}/{to}?apikey={key}",
            "previous_close": "/v2/aggs/ticker/{symbol}/prev?apikey={key}",
            "real_time_quote": "/v1/last_quote/stocks/{symbol}?apikey={key}",
            "company_news": "/v2/reference/news?ticker={symbol}&apikey={key}",
            "market_status": "/v1/marketstatus/now?apikey={key}"
        },
        "rate_limit": "5 calls per minute (free tier)"
    },
    
    "Yahoo Finance": {
        "library": "yfinance",
        "endpoints": {
            "historical_data": "yf.Ticker(symbol).history(period='1y')",
            "company_info": "yf.Ticker(symbol).info",
            "financials": "yf.Ticker(symbol).financials",
            "recommendations": "yf.Ticker(symbol).recommendations",
            "calendar": "yf.Ticker(symbol).calendar"
        },
        "rate_limit": "No official limit, but avoid excessive requests"
    },
    
    "AWS Bedrock": {
        "service": "bedrock-runtime",
        "models": {
            "titan_text": "amazon.titan-text-express-v1",
            "claude_v2": "anthropic.claude-v2",
            "claude_instant": "anthropic.claude-instant-v1"
        },
        "endpoints": {
            "invoke_model": "bedrock.invoke_model(modelId=model_id, body=body)"
        },
        "rate_limit": "Varies by model and region"
    },
    
    "Finnhub": {
        "base_url": "https://finnhub.io/api/v1",
        "endpoints": {
            "quote": "/quote?symbol={symbol}&token={key}",
            "company_profile": "/stock/profile2?symbol={symbol}&token={key}",
            "news": "/company-news?symbol={symbol}&from={from}&to={to}&token={key}",
            "earnings": "/stock/earnings?symbol={symbol}&token={key}",
            "recommendation": "/stock/recommendation?symbol={symbol}&token={key}"
        },
        "rate_limit": "60 calls per minute (free tier)"
    }
}

SAMPLE_API_CALLS = {
    "get_stock_price": """
# Alpha Vantage
import requests
url = "https://www.alphavantage.co/query"
params = {
    'function': 'TIME_SERIES_DAILY',
    'symbol': 'AAPL',
    'apikey': 'YOUR_API_KEY'
}
response = requests.get(url, params=params)
data = response.json()
""",
    
    "get_ai_analysis": """
# AWS Bedrock
import boto3
import json

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
body = json.dumps({
    "inputText": "Analyze AAPL stock performance",
    "textGenerationConfig": {
        "maxTokenCount": 200,
        "temperature": 0.3
    }
})

response = bedrock.invoke_model(
    modelId='amazon.titan-text-express-v1',
    body=body,
    contentType='application/json'
)
""",
    
    "get_news_sentiment": """
# Alpha Vantage News Sentiment
import requests
url = "https://www.alphavantage.co/query"
params = {
    'function': 'NEWS_SENTIMENT',
    'tickers': 'AAPL',
    'apikey': 'YOUR_API_KEY',
    'limit': 10
}
response = requests.get(url, params=params)
news_data = response.json()
"""
}

def get_api_info(api_name):
    """Get API information and endpoints"""
    return API_ENDPOINTS.get(api_name, {})

def get_sample_code(function_name):
    """Get sample API call code"""
    return SAMPLE_API_CALLS.get(function_name, "Sample not available")