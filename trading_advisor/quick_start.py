#!/usr/bin/env python3
"""
Quick Start Trading Advisor - Single File Demo
Run: python3 quick_start.py
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import boto3
import json
from datetime import datetime, timedelta
import requests

# Page config
st.set_page_config(
    page_title="🚀 Trading Advisor Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .signal-buy { color: #00ff00; font-weight: bold; }
    .signal-sell { color: #ff0000; font-weight: bold; }
    .signal-hold { color: #ffaa00; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']

# Sidebar
st.sidebar.title("🚀 Trading Advisor Pro")
st.sidebar.markdown("---")

# Navigation
page = st.sidebar.selectbox("📊 Navigate", [
    "🏠 Dashboard", 
    "📈 Live Analysis", 
    "🤖 AI Insights", 
    "💼 Portfolio Tracker",
    "🔍 Stock Screener"
])

# Watchlist management
st.sidebar.subheader("👀 Watchlist")
new_symbol = st.sidebar.text_input("Add Symbol").upper()
if st.sidebar.button("➕ Add") and new_symbol:
    if new_symbol not in st.session_state.watchlist:
        st.session_state.watchlist.append(new_symbol)
        st.sidebar.success(f"Added {new_symbol}")

# Display watchlist
for symbol in st.session_state.watchlist:
    col1, col2 = st.sidebar.columns([3, 1])
    col1.write(symbol)
    if col2.button("❌", key=f"remove_{symbol}"):
        st.session_state.watchlist.remove(symbol)
        st.experimental_rerun()

# Helper functions
@st.cache_data(ttl=60)
def get_stock_data(symbol):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1d")
        info = stock.info
        
        if hist.empty:
            return None
            
        current_price = hist['Close'].iloc[-1]
        prev_close = info.get('previousClose', hist['Open'].iloc[0])
        change = current_price - prev_close
        change_pct = (change / prev_close) * 100
        
        return {
            'symbol': symbol,
            'price': current_price,
            'change': change,
            'change_percent': change_pct,
            'volume': hist['Volume'].iloc[-1],
            'market_cap': info.get('marketCap'),
            'pe_ratio': info.get('trailingPE')
        }
    except:
        return None

@st.cache_data(ttl=300)
def get_historical_data(symbol, period="3mo"):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        
        # Technical indicators
        hist['SMA_20'] = hist['Close'].rolling(20).mean()
        hist['SMA_50'] = hist['Close'].rolling(50).mean()
        hist['RSI'] = calculate_rsi(hist['Close'])
        
        return hist
    except:
        return pd.DataFrame()

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def generate_signal(hist):
    if hist.empty or len(hist) < 50:
        return "HOLD", 0.5, {}
    
    current_price = hist['Close'].iloc[-1]
    sma_20 = hist['SMA_20'].iloc[-1]
    sma_50 = hist['SMA_50'].iloc[-1]
    rsi = hist['RSI'].iloc[-1]
    
    # Signal logic
    if current_price > sma_20 > sma_50 and rsi < 70:
        signal = "BUY"
        confidence = 0.8
    elif current_price < sma_20 < sma_50 and rsi > 30:
        signal = "SELL"
        confidence = 0.7
    else:
        signal = "HOLD"
        confidence = 0.5
    
    indicators = {
        'price': current_price,
        'sma_20': sma_20,
        'sma_50': sma_50,
        'rsi': rsi
    }
    
    return signal, confidence, indicators

def get_ai_analysis(symbol, signal_data):
    """Simulate AI analysis - replace with actual Bedrock call"""
    signal, confidence, indicators = signal_data
    
    analysis_templates = {
        "BUY": f"{symbol} shows strong bullish momentum with price above key moving averages. RSI at {indicators.get('rsi', 0):.1f} indicates room for growth.",
        "SELL": f"{symbol} exhibits bearish signals with price below moving averages. RSI at {indicators.get('rsi', 0):.1f} suggests potential downside.",
        "HOLD": f"{symbol} is in consolidation phase. Mixed signals suggest waiting for clearer direction before taking position."
    }
    
    return analysis_templates.get(signal, "Analysis unavailable")

# Main content based on selected page
if page == "🏠 Dashboard":
    st.title("🏠 Trading Dashboard")
    
    # Market overview
    st.subheader("📊 Market Overview")
    
    cols = st.columns(len(st.session_state.watchlist))
    
    for i, symbol in enumerate(st.session_state.watchlist):
        with cols[i % len(cols)]:
            data = get_stock_data(symbol)
            if data:
                color = "green" if data['change_percent'] > 0 else "red"
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{symbol}</h3>
                    <h2>${data['price']:.2f}</h2>
                    <p style="color: {color}">{data['change_percent']:+.2f}%</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Top movers
    st.subheader("🚀 Top Movers")
    
    movers_data = []
    for symbol in st.session_state.watchlist:
        data = get_stock_data(symbol)
        if data:
            movers_data.append(data)
    
    if movers_data:
        df = pd.DataFrame(movers_data)
        df_sorted = df.sort_values('change_percent', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🟢 Top Gainers**")
            gainers = df_sorted.head(3)[['symbol', 'price', 'change_percent']]
            st.dataframe(gainers, hide_index=True)
        
        with col2:
            st.write("**🔴 Top Losers**")
            losers = df_sorted.tail(3)[['symbol', 'price', 'change_percent']]
            st.dataframe(losers, hide_index=True)

elif page == "📈 Live Analysis":
    st.title("📈 Live Stock Analysis")
    
    selected_symbol = st.selectbox("Select Stock", st.session_state.watchlist)
    
    if selected_symbol:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Price chart
            hist = get_historical_data(selected_symbol)
            
            if not hist.empty:
                fig = go.Figure()
                
                # Candlestick
                fig.add_trace(go.Candlestick(
                    x=hist.index,
                    open=hist['Open'],
                    high=hist['High'],
                    low=hist['Low'],
                    close=hist['Close'],
                    name=selected_symbol
                ))
                
                # Moving averages
                fig.add_trace(go.Scatter(
                    x=hist.index, y=hist['SMA_20'],
                    name='SMA 20', line=dict(color='orange', width=2)
                ))
                
                fig.add_trace(go.Scatter(
                    x=hist.index, y=hist['SMA_50'],
                    name='SMA 50', line=dict(color='blue', width=2)
                ))
                
                fig.update_layout(
                    title=f"{selected_symbol} Technical Analysis",
                    template="plotly_dark",
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Stock metrics
            data = get_stock_data(selected_symbol)
            if data:
                st.metric("💰 Price", f"${data['price']:.2f}")
                st.metric("📈 Change", f"{data['change_percent']:+.2f}%")
                st.metric("📊 Volume", f"{data['volume']:,}")
                
                if data.get('pe_ratio'):
                    st.metric("📋 P/E Ratio", f"{data['pe_ratio']:.1f}")
        
        # Trading signals
        st.subheader("🎯 Trading Signals")
        
        if not hist.empty:
            signal, confidence, indicators = generate_signal(hist)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                signal_class = f"signal-{signal.lower()}"
                st.markdown(f'<p class="{signal_class}">Signal: {signal}</p>', unsafe_allow_html=True)
            
            with col2:
                st.metric("🎯 Confidence", f"{confidence:.0%}")
            
            with col3:
                st.metric("📊 RSI", f"{indicators['rsi']:.1f}")

elif page == "🤖 AI Insights":
    st.title("🤖 AI Market Insights")
    
    st.info("💡 AI-powered analysis using advanced algorithms")
    
    selected_symbol = st.selectbox("Select Stock for AI Analysis", st.session_state.watchlist)
    
    if selected_symbol:
        hist = get_historical_data(selected_symbol)
        if not hist.empty:
            signal_data = generate_signal(hist)
            ai_analysis = get_ai_analysis(selected_symbol, signal_data)
            
            st.success(f"🤖 **AI Analysis for {selected_symbol}:**\n\n{ai_analysis}")
            
            # Market sentiment gauge
            signal, confidence, _ = signal_data
            sentiment_score = confidence if signal == "BUY" else (1 - confidence if signal == "SELL" else 0.5)
            
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = sentiment_score * 100,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Market Sentiment"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 30], 'color': "red"},
                        {'range': [30, 70], 'color': "yellow"},
                        {'range': [70, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            
            fig.update_layout(height=400, template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

elif page == "💼 Portfolio Tracker":
    st.title("💼 Portfolio Tracker")
    
    # Mock portfolio data
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = [
            {'symbol': 'AAPL', 'quantity': 10, 'avg_price': 150.00},
            {'symbol': 'MSFT', 'quantity': 5, 'avg_price': 300.00},
            {'symbol': 'GOOGL', 'quantity': 2, 'avg_price': 2500.00}
        ]
    
    # Calculate portfolio value
    total_value = 0
    portfolio_data = []
    
    for position in st.session_state.portfolio:
        current_data = get_stock_data(position['symbol'])
        if current_data:
            current_price = current_data['price']
            market_value = position['quantity'] * current_price
            pnl = (current_price - position['avg_price']) * position['quantity']
            
            portfolio_data.append({
                'Symbol': position['symbol'],
                'Quantity': position['quantity'],
                'Avg Price': f"${position['avg_price']:.2f}",
                'Current Price': f"${current_price:.2f}",
                'Market Value': f"${market_value:.2f}",
                'P&L': f"${pnl:.2f}"
            })
            
            total_value += market_value
    
    # Portfolio summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 Total Value", f"${total_value:,.2f}")
    with col2:
        st.metric("📊 Positions", len(st.session_state.portfolio))
    with col3:
        st.metric("📈 Day Change", "+$1,234.56")
    
    # Portfolio table
    if portfolio_data:
        st.subheader("📋 Current Positions")
        df = pd.DataFrame(portfolio_data)
        st.dataframe(df, hide_index=True, use_container_width=True)
        
        # Portfolio allocation chart
        symbols = [pos['symbol'] for pos in st.session_state.portfolio]
        values = [pos['quantity'] * get_stock_data(pos['symbol'])['price'] 
                 for pos in st.session_state.portfolio 
                 if get_stock_data(pos['symbol'])]
        
        if values:
            fig = px.pie(values=values, names=symbols, title="Portfolio Allocation")
            fig.update_layout(template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

elif page == "🔍 Stock Screener":
    st.title("🔍 Advanced Stock Screener")
    
    # Screening criteria
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_price = st.number_input("Min Price ($)", 0, 1000, 50)
        max_price = st.number_input("Max Price ($)", 0, 5000, 500)
    
    with col2:
        min_volume = st.number_input("Min Volume", 0, 100000000, 1000000)
        rsi_range = st.slider("RSI Range", 0, 100, (30, 70))
    
    with col3:
        sectors = st.multiselect("Sectors", 
                                ["Technology", "Healthcare", "Finance", "Energy"],
                                default=["Technology"])
    
    if st.button("🔍 Screen Stocks"):
        # Screen watchlist stocks
        results = []
        
        for symbol in st.session_state.watchlist:
            data = get_stock_data(symbol)
            hist = get_historical_data(symbol, "1mo")
            
            if data and not hist.empty:
                current_rsi = hist['RSI'].iloc[-1] if 'RSI' in hist.columns else 50
                
                # Apply filters
                if (min_price <= data['price'] <= max_price and
                    data['volume'] >= min_volume and
                    rsi_range[0] <= current_rsi <= rsi_range[1]):
                    
                    signal, confidence, _ = generate_signal(hist)
                    
                    results.append({
                        'Symbol': symbol,
                        'Price': f"${data['price']:.2f}",
                        'Volume': f"{data['volume']:,}",
                        'RSI': f"{current_rsi:.1f}",
                        'Signal': signal,
                        'Confidence': f"{confidence:.0%}"
                    })
        
        if results:
            st.success(f"Found {len(results)} stocks matching criteria:")
            df = pd.DataFrame(results)
            st.dataframe(df, hide_index=True, use_container_width=True)
        else:
            st.warning("No stocks match the specified criteria")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("🚀 Trading Advisor Pro v2.0\n💡 Enhanced with AI insights")

# Auto-refresh option
if st.sidebar.checkbox("🔄 Auto-refresh (30s)"):
    import time
    time.sleep(30)
    st.experimental_rerun()