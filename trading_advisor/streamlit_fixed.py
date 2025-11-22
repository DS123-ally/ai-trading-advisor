#!/usr/bin/env python3
"""
Fixed Streamlit Trading App with Real Data
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# Page config
st.set_page_config(
    page_title="📈 Live Trading Advisor",
    page_icon="🚀",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .metric-green { color: #00ff00; }
    .metric-red { color: #ff0000; }
    .big-font { font-size: 24px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def get_stock_data(symbol):
    """Get real stock data"""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if 'chart' in data and data['chart']['result']:
            result = data['chart']['result'][0]
            meta = result['meta']
            
            current_price = meta['regularMarketPrice']
            prev_close = meta['previousClose']
            change = current_price - prev_close
            change_pct = (change / prev_close) * 100
            
            return {
                'symbol': symbol,
                'price': round(current_price, 2),
                'change': round(change, 2),
                'change_percent': round(change_pct, 2),
                'volume': meta.get('regularMarketVolume', 0),
                'high': meta.get('regularMarketDayHigh', current_price),
                'low': meta.get('regularMarketDayLow', current_price)
            }
    except:
        pass
    
    return None

@st.cache_data(ttl=300)
def get_historical_data(symbol):
    """Get historical data for charts"""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1mo&interval=1d"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if 'chart' in data and data['chart']['result']:
            result = data['chart']['result'][0]
            timestamps = result['timestamp']
            quotes = result['indicators']['quote'][0]
            
            df = pd.DataFrame({
                'Date': pd.to_datetime(timestamps, unit='s'),
                'Open': quotes['open'],
                'High': quotes['high'],
                'Low': quotes['low'],
                'Close': quotes['close'],
                'Volume': quotes['volume']
            })
            
            return df.dropna()
    except:
        pass
    
    return pd.DataFrame()

def generate_signal(data):
    """Generate trading signal"""
    if not data:
        return "HOLD", 0.5
    
    change_pct = data['change_percent']
    
    if change_pct > 2:
        return "BUY", 0.8
    elif change_pct < -2:
        return "SELL", 0.8
    else:
        return "HOLD", 0.5

# Main app
st.title("🚀 Live Trading Advisor")
st.markdown("📡 **Real-time market data & analysis**")

# Sidebar
st.sidebar.title("📊 Controls")

# Watchlist
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']

# Add/remove stocks
new_symbol = st.sidebar.text_input("Add Stock Symbol").upper()
if st.sidebar.button("➕ Add") and new_symbol:
    if new_symbol not in st.session_state.watchlist:
        st.session_state.watchlist.append(new_symbol)
        st.rerun()

# Auto-refresh
auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (30s)")

# Main content tabs
tab1, tab2, tab3 = st.tabs(["📊 Market Overview", "📈 Stock Analysis", "🎯 Top Movers"])

with tab1:
    st.subheader("📊 Live Market Data")
    
    # Market overview cards
    cols = st.columns(len(st.session_state.watchlist))
    
    for i, symbol in enumerate(st.session_state.watchlist):
        with cols[i % len(cols)]:
            data = get_stock_data(symbol)
            
            if data:
                signal, confidence = generate_signal(data)
                
                # Color based on change
                color = "green" if data['change_percent'] > 0 else "red"
                
                st.metric(
                    label=f"**{symbol}**",
                    value=f"${data['price']}",
                    delta=f"{data['change_percent']:+.2f}%"
                )
                
                # Signal indicator
                signal_color = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}
                st.write(f"{signal_color[signal]} **{signal}** ({confidence:.0%})")
                
                # Remove button
                if st.button(f"❌", key=f"remove_{symbol}"):
                    st.session_state.watchlist.remove(symbol)
                    st.rerun()
            else:
                st.error(f"❌ {symbol} - No data")
    
    # Market summary table
    st.subheader("📋 Detailed View")
    
    market_data = []
    for symbol in st.session_state.watchlist:
        data = get_stock_data(symbol)
        if data:
            signal, confidence = generate_signal(data)
            market_data.append({
                'Symbol': symbol,
                'Price': f"${data['price']}",
                'Change': f"{data['change_percent']:+.2f}%",
                'Volume': f"{data['volume']:,}",
                'High': f"${data['high']}",
                'Low': f"${data['low']}",
                'Signal': signal
            })
    
    if market_data:
        df = pd.DataFrame(market_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("📈 Individual Stock Analysis")
    
    # Stock selection
    selected_symbol = st.selectbox("Select Stock", st.session_state.watchlist)
    
    if selected_symbol:
        data = get_stock_data(selected_symbol)
        
        if data:
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("💰 Price", f"${data['price']}")
            with col2:
                st.metric("📊 Change", f"{data['change_percent']:+.2f}%")
            with col3:
                st.metric("📦 Volume", f"{data['volume']:,}")
            with col4:
                signal, confidence = generate_signal(data)
                st.metric("🎯 Signal", signal)
            
            # Price chart
            hist_data = get_historical_data(selected_symbol)
            
            if not hist_data.empty:
                fig = go.Figure()
                
                fig.add_trace(go.Candlestick(
                    x=hist_data['Date'],
                    open=hist_data['Open'],
                    high=hist_data['High'],
                    low=hist_data['Low'],
                    close=hist_data['Close'],
                    name=selected_symbol
                ))
                
                fig.update_layout(
                    title=f"{selected_symbol} - 1 Month Chart",
                    template="plotly_dark",
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Analysis
            st.subheader("🔍 Analysis")
            
            support = data['price'] * 0.95
            resistance = data['price'] * 1.05
            risk = "High" if abs(data['change_percent']) > 3 else "Medium" if abs(data['change_percent']) > 1 else "Low"
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**📊 Technical Levels:**")
                st.write(f"• Support: ${support:.2f}")
                st.write(f"• Resistance: ${resistance:.2f}")
                st.write(f"• Day Range: ${data['low']} - ${data['high']}")
            
            with col2:
                st.write("**⚖️ Risk Assessment:**")
                st.write(f"• Risk Level: {risk}")
                st.write(f"• Volatility: {abs(data['change_percent']):.2f}%")
                st.write(f"• Signal Confidence: {confidence:.0%}")

with tab3:
    st.subheader("🎯 Top Movers")
    
    # Get all data and sort by movement
    all_data = []
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'AMZN', 'META', 'NFLX', 'AMD']
    
    for symbol in symbols:
        data = get_stock_data(symbol)
        if data:
            all_data.append(data)
    
    # Sort by absolute change
    all_data.sort(key=lambda x: abs(x['change_percent']), reverse=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**🟢 Top Gainers:**")
        gainers = [d for d in all_data if d['change_percent'] > 0][:5]
        for data in gainers:
            st.write(f"🟢 **{data['symbol']}**: ${data['price']} (+{data['change_percent']:.2f}%)")
    
    with col2:
        st.write("**🔴 Top Losers:**")
        losers = [d for d in all_data if d['change_percent'] < 0][:5]
        for data in losers:
            st.write(f"🔴 **{data['symbol']}**: ${data['price']} ({data['change_percent']:.2f}%)")

# Footer
st.sidebar.markdown("---")
st.sidebar.info(f"🕐 Last updated: {datetime.now().strftime('%H:%M:%S')}")

# Auto-refresh
if auto_refresh:
    time.sleep(30)
    st.rerun()