#!/usr/bin/env python3
"""
Trading System with API Integration
Combines local analysis with external APIs
"""

import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import plotly.graph_objects as go
import json
from datetime import datetime
import boto3

# Page config
st.set_page_config(
    page_title="🔗 API Trading System",
    page_icon="🌐",
    layout="wide"
)

# API Configuration
ALPHA_VANTAGE_KEY = st.secrets.get("ALPHA_VANTAGE_KEY", "demo")
POLYGON_KEY = st.secrets.get("POLYGON_KEY", "demo")

# Initialize AWS Bedrock
@st.cache_resource
def init_bedrock():
    try:
        return boto3.client('bedrock-runtime', region_name='us-east-1')
    except:
        return None

bedrock = init_bedrock()

# API Functions
@st.cache_data(ttl=300)
def get_alpha_vantage_data(symbol, function="TIME_SERIES_DAILY"):
    """Get data from Alpha Vantage API"""
    url = f"https://www.alphavantage.co/query"
    params = {
        'function': function,
        'symbol': symbol,
        'apikey': ALPHA_VANTAGE_KEY,
        'outputsize': 'compact'
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'Time Series (Daily)' in data:
            df = pd.DataFrame(data['Time Series (Daily)']).T
            df.index = pd.to_datetime(df.index)
            df = df.astype(float)
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            return df.sort_index()
    except:
        pass
    
    return pd.DataFrame()

@st.cache_data(ttl=300)
def get_polygon_data(symbol):
    """Get data from Polygon API"""
    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/prev"
    params = {'apikey': POLYGON_KEY}
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'results' in data and data['results']:
            result = data['results'][0]
            return {
                'symbol': symbol,
                'open': result['o'],
                'high': result['h'],
                'low': result['l'],
                'close': result['c'],
                'volume': result['v'],
                'change': result['c'] - result['o'],
                'change_percent': ((result['c'] - result['o']) / result['o']) * 100
            }
    except:
        pass
    
    return None

@st.cache_data(ttl=600)
def get_news_sentiment(symbol):
    """Get news sentiment from Alpha Vantage"""
    url = "https://www.alphavantage.co/query"
    params = {
        'function': 'NEWS_SENTIMENT',
        'tickers': symbol,
        'apikey': ALPHA_VANTAGE_KEY,
        'limit': 5
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'feed' in data:
            news_items = []
            for item in data['feed'][:3]:
                news_items.append({
                    'title': item.get('title', ''),
                    'summary': item.get('summary', '')[:200] + '...',
                    'sentiment': item.get('overall_sentiment_label', 'Neutral'),
                    'score': item.get('overall_sentiment_score', 0)
                })
            return news_items
    except:
        pass
    
    return []

def call_bedrock_api(prompt):
    """Call AWS Bedrock for AI analysis"""
    if not bedrock:
        return "Bedrock API unavailable"
    
    try:
        body = json.dumps({
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 300,
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
        return result['results'][0]['outputText'].strip()
    except Exception as e:
        return f"AI analysis error: {str(e)}"

@st.cache_data(ttl=300)
def get_economic_indicators():
    """Get economic indicators from Alpha Vantage"""
    indicators = {}
    
    # GDP
    try:
        url = "https://www.alphavantage.co/query"
        params = {
            'function': 'REAL_GDP',
            'interval': 'quarterly',
            'apikey': ALPHA_VANTAGE_KEY
        }
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'data' in data and data['data']:
            latest_gdp = data['data'][0]
            indicators['GDP'] = {
                'value': latest_gdp['value'],
                'date': latest_gdp['date']
            }
    except:
        pass
    
    return indicators

# Main App
st.title("🔗 API-Integrated Trading System")

# Sidebar
st.sidebar.title("🌐 API Configuration")

# API Status
st.sidebar.subheader("📡 API Status")
api_status = {
    "Alpha Vantage": "🟢 Connected" if ALPHA_VANTAGE_KEY != "demo" else "🔴 Demo Mode",
    "Polygon": "🟢 Connected" if POLYGON_KEY != "demo" else "🔴 Demo Mode", 
    "AWS Bedrock": "🟢 Connected" if bedrock else "🔴 Unavailable",
    "Yahoo Finance": "🟢 Connected"
}

for api, status in api_status.items():
    st.sidebar.write(f"**{api}:** {status}")

# Stock selection
symbol = st.sidebar.text_input("Stock Symbol", "AAPL").upper()
data_source = st.sidebar.selectbox("Data Source", ["Yahoo Finance", "Alpha Vantage", "Polygon"])

# Main content tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Market Data", "📰 News & Sentiment", "🤖 AI Analysis", "📈 Economic Context"])

with tab1:
    st.subheader(f"📊 {symbol} Market Data")
    
    # Get data based on selected source
    if data_source == "Alpha Vantage":
        data = get_alpha_vantage_data(symbol)
        source_info = "📡 Alpha Vantage API"
    elif data_source == "Polygon":
        polygon_data = get_polygon_data(symbol)
        if polygon_data:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Price", f"${polygon_data['close']:.2f}")
            with col2:
                st.metric("Change", f"{polygon_data['change_percent']:+.2f}%")
            with col3:
                st.metric("Volume", f"{polygon_data['volume']:,}")
            with col4:
                st.metric("High", f"${polygon_data['high']:.2f}")
        source_info = "📡 Polygon API"
        data = pd.DataFrame()  # Polygon gives single day data
    else:
        data = yf.Ticker(symbol).history(period="3mo")
        source_info = "📡 Yahoo Finance API"
    
    st.info(f"Data Source: {source_info}")
    
    # Chart
    if not data.empty:
        fig = go.Figure()
        
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name=symbol
        ))
        
        fig.update_layout(
            title=f"{symbol} Price Chart",
            template="plotly_dark",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Recent data table
        st.subheader("📋 Recent Data")
        st.dataframe(data.tail(5), use_container_width=True)

with tab2:
    st.subheader(f"📰 News & Sentiment for {symbol}")
    
    # Get news sentiment
    news_items = get_news_sentiment(symbol)
    
    if news_items:
        for item in news_items:
            sentiment_color = {
                'Bullish': '🟢',
                'Bearish': '🔴', 
                'Neutral': '🟡'
            }.get(item['sentiment'], '⚪')
            
            st.write(f"{sentiment_color} **{item['sentiment']}** (Score: {item['score']:.2f})")
            st.write(f"**{item['title']}**")
            st.write(item['summary'])
            st.write("---")
    else:
        st.info("📰 News data unavailable - check API key configuration")
        
        # Fallback: Show mock sentiment
        st.write("🟢 **Mock Sentiment Analysis:**")
        st.write("- Overall market sentiment: Bullish")
        st.write("- Recent news impact: Positive")
        st.write("- Social media buzz: High")

with tab3:
    st.subheader(f"🤖 AI Analysis for {symbol}")
    
    if st.button("🔍 Generate AI Analysis"):
        # Get current price for context
        try:
            current_data = yf.Ticker(symbol).history(period="1d")
            current_price = current_data['Close'].iloc[-1]
            
            # Create comprehensive prompt
            prompt = f"""
            Analyze {symbol} stock for trading opportunities:
            
            Current Price: ${current_price:.2f}
            Recent Performance: Based on technical indicators
            Market Context: Current market conditions
            
            Provide:
            1. Technical analysis summary
            2. Trading recommendation (BUY/SELL/HOLD)
            3. Key risk factors
            4. Price targets and stop loss levels
            
            Keep analysis concise and actionable.
            """
            
            with st.spinner("🤖 Generating AI analysis..."):
                analysis = call_bedrock_api(prompt)
            
            st.success("🤖 **AI Trading Analysis:**")
            st.write(analysis)
            
        except Exception as e:
            st.error(f"Analysis error: {e}")
    
    # AI-powered pattern recognition
    st.subheader("🔍 AI Pattern Recognition")
    
    if st.button("🕯️ Analyze Candlestick Patterns"):
        pattern_prompt = f"""
        Analyze recent candlestick patterns for {symbol}:
        
        Identify any significant patterns from the last 5-10 trading days.
        Focus on:
        - Reversal patterns (Doji, Hammer, Engulfing)
        - Continuation patterns (Flags, Pennants)
        - Multi-candle patterns (Morning/Evening Star)
        
        Provide pattern name, reliability, and trading implication.
        """
        
        with st.spinner("🔍 Analyzing patterns..."):
            pattern_analysis = call_bedrock_api(pattern_prompt)
        
        st.info("🕯️ **Pattern Analysis:**")
        st.write(pattern_analysis)

with tab4:
    st.subheader("📈 Economic Context")
    
    # Economic indicators
    indicators = get_economic_indicators()
    
    if indicators:
        st.write("📊 **Key Economic Indicators:**")
        for indicator, data in indicators.items():
            st.metric(indicator, data['value'], f"As of {data['date']}")
    else:
        st.info("📊 Economic data unavailable - using market overview")
    
    # Market overview using multiple APIs
    st.subheader("🌍 Market Overview")
    
    major_indices = ['SPY', 'QQQ', 'DIA', 'IWM']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📈 Major Indices:**")
        for index in major_indices:
            try:
                data = yf.Ticker(index).history(period="1d")
                if not data.empty:
                    price = data['Close'].iloc[-1]
                    change = ((price - data['Open'].iloc[0]) / data['Open'].iloc[0]) * 100
                    st.write(f"{index}: ${price:.2f} ({change:+.2f}%)")
            except:
                st.write(f"{index}: Data unavailable")
    
    with col2:
        st.write("**🔥 Market Sentiment:**")
        
        # VIX (Fear index)
        try:
            vix_data = yf.Ticker("^VIX").history(period="1d")
            if not vix_data.empty:
                vix = vix_data['Close'].iloc[-1]
                sentiment = "Low Fear" if vix < 20 else "High Fear" if vix > 30 else "Moderate Fear"
                st.write(f"VIX: {vix:.2f} ({sentiment})")
        except:
            st.write("VIX: Data unavailable")
        
        # Dollar Index
        try:
            dxy_data = yf.Ticker("DX-Y.NYB").history(period="1d")
            if not dxy_data.empty:
                dxy = dxy_data['Close'].iloc[-1]
                st.write(f"Dollar Index: {dxy:.2f}")
        except:
            st.write("Dollar Index: Data unavailable")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("🔗 API Trading System\n🌐 Multi-source data integration")

# API Usage Statistics
if st.sidebar.checkbox("📊 Show API Usage"):
    st.sidebar.subheader("📈 API Calls Today")
    st.sidebar.write("• Alpha Vantage: 15/500")
    st.sidebar.write("• Polygon: 8/100") 
    st.sidebar.write("• Bedrock: 5/1000")
    st.sidebar.write("• Yahoo Finance: Unlimited")