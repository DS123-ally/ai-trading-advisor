#!/usr/bin/env python3
"""
Complete Trading App with Dashboard, Analysis & AI Chatbot
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import json

# Page config
st.set_page_config(
    page_title="🚀 Complete Trading Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        background: #f0f2f6;
    }
    .user-message {
        background: #e3f2fd;
        text-align: right;
    }
    .bot-message {
        background: #f3e5f5;
    }
    .signal-buy { color: #00ff00; font-weight: bold; }
    .signal-sell { color: #ff0000; font-weight: bold; }
    .signal-hold { color: #ffaa00; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = [
        {'symbol': 'AAPL', 'shares': 10, 'avg_price': 180.00},
        {'symbol': 'MSFT', 'shares': 5, 'avg_price': 375.00},
        {'symbol': 'GOOGL', 'shares': 2, 'avg_price': 140.00}
    ]

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
                'low': meta.get('regularMarketDayLow', current_price),
                'market_cap': meta.get('marketCap', 0)
            }
    except:
        pass
    
    return None

@st.cache_data(ttl=300)
def get_historical_data(symbol, period="1mo"):
    """Get historical data for charts"""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range={period}&interval=1d"
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
            
            # Add technical indicators
            df['SMA_20'] = df['Close'].rolling(20).mean()
            df['SMA_50'] = df['Close'].rolling(50).mean()
            df['RSI'] = calculate_rsi(df['Close'])
            
            return df.dropna()
    except:
        pass
    
    return pd.DataFrame()

def calculate_rsi(prices, period=14):
    """Calculate RSI"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def generate_signal(data, hist_data=None):
    """Generate advanced trading signal"""
    if not data:
        return "HOLD", 0.5, "No data available"
    
    change_pct = data['change_percent']
    
    # Basic momentum signal
    if change_pct > 3:
        return "BUY", 0.9, f"Strong upward momentum (+{change_pct:.1f}%)"
    elif change_pct < -3:
        return "SELL", 0.9, f"Strong downward momentum ({change_pct:.1f}%)"
    elif change_pct > 1:
        return "BUY", 0.6, f"Moderate bullish trend (+{change_pct:.1f}%)"
    elif change_pct < -1:
        return "SELL", 0.6, f"Moderate bearish trend ({change_pct:.1f}%)"
    else:
        return "HOLD", 0.5, f"Sideways movement ({change_pct:.1f}%)"

def ai_chatbot_response(user_message, market_context=None):
    """Generate AI chatbot response"""
    user_message = user_message.lower()
    
    # Stock price queries
    if any(symbol.lower() in user_message for symbol in ['aapl', 'apple']):
        data = get_stock_data('AAPL')
        if data:
            return f"🍎 AAPL is currently trading at ${data['price']} ({data['change_percent']:+.2f}%). The stock is showing {'bullish' if data['change_percent'] > 0 else 'bearish'} momentum today."
    
    elif any(symbol.lower() in user_message for symbol in ['tsla', 'tesla']):
        data = get_stock_data('TSLA')
        if data:
            return f"⚡ TSLA is at ${data['price']} ({data['change_percent']:+.2f}%). Tesla's volatility makes it a high-risk, high-reward play."
    
    elif any(symbol.lower() in user_message for symbol in ['nvda', 'nvidia']):
        data = get_stock_data('NVDA')
        if data:
            return f"🎮 NVDA is trading at ${data['price']} ({data['change_percent']:+.2f}%). NVIDIA benefits from AI and gaming trends."
    
    # General trading questions
    elif 'buy' in user_message or 'purchase' in user_message:
        return "💡 Before buying: 1) Check the trend 2) Set stop-loss 3) Don't invest more than you can afford to lose 4) Diversify your portfolio"
    
    elif 'sell' in user_message:
        return "📉 Consider selling when: 1) Stock hits your target price 2) Fundamentals deteriorate 3) Better opportunities arise 4) Risk management requires it"
    
    elif 'portfolio' in user_message:
        return "💼 Good portfolio management: 1) Diversify across sectors 2) Regular rebalancing 3) Risk management 4) Long-term perspective 5) Don't panic sell"
    
    elif 'risk' in user_message:
        return "⚖️ Risk management tips: 1) Never risk more than 2% per trade 2) Use stop-losses 3) Position sizing based on volatility 4) Diversification is key"
    
    elif 'market' in user_message or 'trend' in user_message:
        return "📊 Current market analysis: Monitor key indicators like VIX, sector rotation, earnings reports, and Fed policy. Stay informed but don't overtrade!"
    
    elif 'help' in user_message:
        return "🤖 I can help with: Stock prices, trading strategies, portfolio advice, risk management, market analysis. Try asking about specific stocks or trading concepts!"
    
    else:
        return "🤔 I'm here to help with trading questions! Ask me about stock prices, trading strategies, portfolio management, or market analysis."

# Sidebar
st.sidebar.title("🚀 Trading Platform")
st.sidebar.markdown("---")

# Navigation
page = st.sidebar.selectbox("📊 Navigate", [
    "🏠 Dashboard", 
    "📈 Advanced Analysis", 
    "💼 Portfolio Manager",
    "🤖 AI Trading Assistant",
    "🔍 Stock Screener"
])

# Watchlist management
st.sidebar.subheader("👀 Watchlist")
new_symbol = st.sidebar.text_input("Add Symbol").upper()
if st.sidebar.button("➕ Add") and new_symbol:
    if new_symbol not in st.session_state.watchlist:
        st.session_state.watchlist.append(new_symbol)
        st.rerun()

for symbol in st.session_state.watchlist:
    col1, col2 = st.sidebar.columns([3, 1])
    col1.write(symbol)
    if col2.button("❌", key=f"remove_{symbol}"):
        st.session_state.watchlist.remove(symbol)
        st.rerun()

# Main content
if page == "🏠 Dashboard":
    st.title("🏠 Trading Dashboard")
    st.markdown("📊 **Real-time market overview & key metrics**")
    
    # Market overview cards
    st.subheader("📈 Market Overview")
    cols = st.columns(len(st.session_state.watchlist))
    
    total_market_cap = 0
    market_data = []
    
    for i, symbol in enumerate(st.session_state.watchlist):
        with cols[i % len(cols)]:
            data = get_stock_data(symbol)
            
            if data:
                signal, confidence, reason = generate_signal(data)
                market_data.append(data)
                total_market_cap += data.get('market_cap', 0)
                
                # Metric card
                color = "green" if data['change_percent'] > 0 else "red"
                st.metric(
                    label=f"**{symbol}**",
                    value=f"${data['price']}",
                    delta=f"{data['change_percent']:+.2f}%"
                )
                
                # Signal
                signal_class = f"signal-{signal.lower()}"
                st.markdown(f'<p class="{signal_class}">{signal} ({confidence:.0%})</p>', unsafe_allow_html=True)
    
    # Market summary
    st.subheader("📊 Market Summary")
    
    if market_data:
        avg_change = sum([d['change_percent'] for d in market_data]) / len(market_data)
        total_volume = sum([d['volume'] for d in market_data])
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📈 Avg Change", f"{avg_change:+.2f}%")
        with col2:
            st.metric("📦 Total Volume", f"{total_volume:,}")
        with col3:
            st.metric("🏢 Stocks Tracked", len(market_data))
        with col4:
            bullish_count = sum([1 for d in market_data if d['change_percent'] > 0])
            st.metric("🟢 Bullish", f"{bullish_count}/{len(market_data)}")
    
    # Price chart
    st.subheader("📈 Price Trends")
    
    selected_for_chart = st.selectbox("Select stock for chart", st.session_state.watchlist)
    hist_data = get_historical_data(selected_for_chart)
    
    if not hist_data.empty:
        fig = go.Figure()
        
        fig.add_trace(go.Candlestick(
            x=hist_data['Date'],
            open=hist_data['Open'],
            high=hist_data['High'],
            low=hist_data['Low'],
            close=hist_data['Close'],
            name=selected_for_chart
        ))
        
        # Add moving averages
        fig.add_trace(go.Scatter(
            x=hist_data['Date'], 
            y=hist_data['SMA_20'],
            name='SMA 20',
            line=dict(color='orange', width=1)
        ))
        
        fig.update_layout(
            title=f"{selected_for_chart} - Price & Moving Averages",
            template="plotly_dark",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

elif page == "📈 Advanced Analysis":
    st.title("📈 Advanced Technical Analysis")
    
    selected_symbol = st.selectbox("Select Stock for Analysis", st.session_state.watchlist)
    
    if selected_symbol:
        data = get_stock_data(selected_symbol)
        hist_data = get_historical_data(selected_symbol, "3mo")
        
        if data and not hist_data.empty:
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("💰 Current Price", f"${data['price']}")
            with col2:
                st.metric("📊 Change", f"{data['change_percent']:+.2f}%")
            with col3:
                st.metric("📦 Volume", f"{data['volume']:,}")
            with col4:
                signal, confidence, reason = generate_signal(data, hist_data)
                st.metric("🎯 Signal", f"{signal} ({confidence:.0%})")
            
            # Technical analysis
            st.subheader("🔍 Technical Indicators")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Price chart with indicators
                fig = go.Figure()
                
                fig.add_trace(go.Candlestick(
                    x=hist_data['Date'],
                    open=hist_data['Open'],
                    high=hist_data['High'],
                    low=hist_data['Low'],
                    close=hist_data['Close'],
                    name=selected_symbol
                ))
                
                fig.add_trace(go.Scatter(
                    x=hist_data['Date'], y=hist_data['SMA_20'],
                    name='SMA 20', line=dict(color='orange')
                ))
                
                fig.add_trace(go.Scatter(
                    x=hist_data['Date'], y=hist_data['SMA_50'],
                    name='SMA 50', line=dict(color='blue')
                ))
                
                fig.update_layout(
                    title="Price Chart with Moving Averages",
                    template="plotly_dark",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # RSI chart
                fig_rsi = go.Figure()
                
                fig_rsi.add_trace(go.Scatter(
                    x=hist_data['Date'],
                    y=hist_data['RSI'],
                    name='RSI',
                    line=dict(color='purple')
                ))
                
                fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
                fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")
                
                fig_rsi.update_layout(
                    title="RSI Indicator",
                    template="plotly_dark",
                    height=400,
                    yaxis=dict(range=[0, 100])
                )
                
                st.plotly_chart(fig_rsi, use_container_width=True)
            
            # Analysis summary
            st.subheader("📋 Analysis Summary")
            
            current_rsi = hist_data['RSI'].iloc[-1]
            current_sma_20 = hist_data['SMA_20'].iloc[-1]
            current_sma_50 = hist_data['SMA_50'].iloc[-1]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**📊 Current Levels:**")
                st.write(f"• Price: ${data['price']}")
                st.write(f"• SMA 20: ${current_sma_20:.2f}")
                st.write(f"• SMA 50: ${current_sma_50:.2f}")
                st.write(f"• RSI: {current_rsi:.1f}")
            
            with col2:
                st.write("**🎯 Support & Resistance:**")
                support = data['price'] * 0.95
                resistance = data['price'] * 1.05
                st.write(f"• Support: ${support:.2f}")
                st.write(f"• Resistance: ${resistance:.2f}")
                st.write(f"• Day High: ${data['high']}")
                st.write(f"• Day Low: ${data['low']}")
            
            with col3:
                st.write("**⚖️ Risk Assessment:**")
                volatility = abs(data['change_percent'])
                risk = "High" if volatility > 3 else "Medium" if volatility > 1 else "Low"
                st.write(f"• Risk Level: {risk}")
                st.write(f"• Volatility: {volatility:.2f}%")
                st.write(f"• Signal: {signal}")
                st.write(f"• Confidence: {confidence:.0%}")

elif page == "💼 Portfolio Manager":
    st.title("💼 Portfolio Management")
    
    # Portfolio overview
    st.subheader("📊 Portfolio Overview")
    
    total_value = 0
    total_cost = 0
    portfolio_data = []
    
    for position in st.session_state.portfolio:
        current_data = get_stock_data(position['symbol'])
        if current_data:
            current_value = position['shares'] * current_data['price']
            cost_basis = position['shares'] * position['avg_price']
            pnl = current_value - cost_basis
            pnl_pct = (pnl / cost_basis) * 100
            
            total_value += current_value
            total_cost += cost_basis
            
            portfolio_data.append({
                'Symbol': position['symbol'],
                'Shares': position['shares'],
                'Avg Price': f"${position['avg_price']:.2f}",
                'Current Price': f"${current_data['price']:.2f}",
                'Market Value': f"${current_value:,.2f}",
                'P&L': f"${pnl:+,.2f}",
                'P&L %': f"{pnl_pct:+.1f}%"
            })
    
    total_pnl = total_value - total_cost
    total_pnl_pct = (total_pnl / total_cost) * 100 if total_cost > 0 else 0
    
    # Portfolio metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Total Value", f"${total_value:,.2f}")
    with col2:
        st.metric("💸 Total Cost", f"${total_cost:,.2f}")
    with col3:
        st.metric("📈 Total P&L", f"${total_pnl:+,.2f}")
    with col4:
        st.metric("📊 P&L %", f"{total_pnl_pct:+.1f}%")
    
    # Portfolio table
    if portfolio_data:
        st.dataframe(pd.DataFrame(portfolio_data), use_container_width=True, hide_index=True)
        
        # Portfolio allocation chart
        symbols = [pos['symbol'] for pos in st.session_state.portfolio]
        values = [pos['shares'] * get_stock_data(pos['symbol'])['price'] 
                 for pos in st.session_state.portfolio 
                 if get_stock_data(pos['symbol'])]
        
        if values:
            fig = px.pie(values=values, names=symbols, title="Portfolio Allocation")
            fig.update_layout(template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

elif page == "🤖 AI Trading Assistant":
    st.title("🤖 AI Trading Assistant")
    st.markdown("💬 **Ask me anything about trading, stocks, or market analysis!**")
    
    # Chat interface
    st.subheader("💬 Chat with AI Assistant")
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message['type'] == 'user':
            st.markdown(f'<div class="chat-message user-message">👤 You: {message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message bot-message">🤖 Assistant: {message["content"]}</div>', unsafe_allow_html=True)
    
    # Chat input
    user_input = st.text_input("Ask me about stocks, trading strategies, or market analysis:", key="chat_input")
    
    if st.button("Send") and user_input:
        # Add user message
        st.session_state.chat_history.append({
            'type': 'user',
            'content': user_input,
            'timestamp': datetime.now()
        })
        
        # Generate AI response
        ai_response = ai_chatbot_response(user_input)
        
        # Add AI response
        st.session_state.chat_history.append({
            'type': 'bot',
            'content': ai_response,
            'timestamp': datetime.now()
        })
        
        st.rerun()
    
    # Quick questions
    st.subheader("🚀 Quick Questions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📈 Market Trend"):
            st.session_state.chat_history.append({
                'type': 'user',
                'content': 'What is the current market trend?',
                'timestamp': datetime.now()
            })
            st.session_state.chat_history.append({
                'type': 'bot',
                'content': ai_chatbot_response('market trend'),
                'timestamp': datetime.now()
            })
            st.rerun()
    
    with col2:
        if st.button("💼 Portfolio Tips"):
            st.session_state.chat_history.append({
                'type': 'user',
                'content': 'Give me portfolio management tips',
                'timestamp': datetime.now()
            })
            st.session_state.chat_history.append({
                'type': 'bot',
                'content': ai_chatbot_response('portfolio tips'),
                'timestamp': datetime.now()
            })
            st.rerun()
    
    with col3:
        if st.button("⚖️ Risk Management"):
            st.session_state.chat_history.append({
                'type': 'user',
                'content': 'How to manage trading risk?',
                'timestamp': datetime.now()
            })
            st.session_state.chat_history.append({
                'type': 'bot',
                'content': ai_chatbot_response('risk management'),
                'timestamp': datetime.now()
            })
            st.rerun()

elif page == "🔍 Stock Screener":
    st.title("🔍 Advanced Stock Screener")
    
    # Screening criteria
    st.subheader("📋 Screening Criteria")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_price = st.number_input("Min Price ($)", 0, 1000, 50)
        max_price = st.number_input("Max Price ($)", 0, 2000, 500)
    
    with col2:
        min_change = st.number_input("Min Change (%)", -20.0, 20.0, -5.0)
        max_change = st.number_input("Max Change (%)", -20.0, 20.0, 5.0)
    
    with col3:
        min_volume = st.number_input("Min Volume", 0, 100000000, 1000000)
    
    if st.button("🔍 Screen Stocks"):
        # Extended symbol list for screening
        all_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'AMZN', 'META', 'NFLX', 
                      'AMD', 'INTC', 'CRM', 'ORCL', 'ADBE', 'PYPL', 'UBER', 'LYFT',
                      'SNAP', 'TWTR', 'ZOOM', 'SHOP', 'SQ', 'ROKU', 'PINS']
        
        results = []
        progress_bar = st.progress(0)
        
        for i, symbol in enumerate(all_symbols):
            data = get_stock_data(symbol)
            
            if data and (min_price <= data['price'] <= max_price and
                        min_change <= data['change_percent'] <= max_change and
                        data['volume'] >= min_volume):
                
                signal, confidence, reason = generate_signal(data)
                
                results.append({
                    'Symbol': symbol,
                    'Price': f"${data['price']}",
                    'Change %': f"{data['change_percent']:+.2f}%",
                    'Volume': f"{data['volume']:,}",
                    'Signal': signal,
                    'Confidence': f"{confidence:.0%}"
                })
            
            progress_bar.progress((i + 1) / len(all_symbols))
        
        if results:
            st.success(f"✅ Found {len(results)} stocks matching criteria:")
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("❌ No stocks match the specified criteria")

# Footer
st.sidebar.markdown("---")
st.sidebar.info(f"🕐 Last updated: {datetime.now().strftime('%H:%M:%S')}")
st.sidebar.markdown("🚀 **Complete Trading Platform**")
st.sidebar.markdown("📊 Real-time data & AI analysis")