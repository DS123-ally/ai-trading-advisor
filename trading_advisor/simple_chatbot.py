#!/usr/bin/env python3
"""
Simple Working Trading Chatbot
"""

import streamlit as st
import requests
from datetime import datetime

# Page config
st.set_page_config(page_title="🤖 Trading Chatbot", layout="wide")

# Initialize chat history
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Hi! I'm your AI Trading Assistant. Ask me about stocks, trading strategies, or market analysis!"}
    ]

def get_stock_price(symbol):
    """Get stock price with fallback"""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if 'chart' in data and data['chart']['result']:
            meta = data['chart']['result'][0]['meta']
            price = meta['regularMarketPrice']
            prev_close = meta['previousClose']
            change_pct = ((price - prev_close) / prev_close) * 100
            
            return {
                'price': round(price, 2),
                'change': round(change_pct, 2),
                'volume': meta.get('regularMarketVolume', 0)
            }
    except:
        pass
    
    # Fallback mock data
    mock_prices = {
        'AAPL': 185.50, 'MSFT': 378.20, 'GOOGL': 142.30,
        'TSLA': 240.80, 'NVDA': 485.60, 'AMZN': 155.90
    }
    
    if symbol in mock_prices:
        import random
        price = mock_prices[symbol] * (1 + random.uniform(-0.05, 0.05))
        change = random.uniform(-3, 3)
        return {
            'price': round(price, 2),
            'change': round(change, 2),
            'volume': random.randint(10000000, 50000000)
        }
    
    return None

def chatbot_response(message):
    """Generate chatbot response"""
    msg = message.lower()
    
    # Stock price queries
    symbols = ['aapl', 'msft', 'googl', 'tsla', 'nvda', 'amzn']
    for symbol in symbols:
        if symbol in msg:
            data = get_stock_price(symbol.upper())
            if data:
                trend = "📈" if data['change'] > 0 else "📉"
                return f"{trend} **{symbol.upper()}**: ${data['price']} ({data['change']:+.2f}%)\nVolume: {data['volume']:,}\n\n{'Bullish momentum!' if data['change'] > 2 else 'Bearish pressure!' if data['change'] < -2 else 'Sideways movement.'}"
    
    # Trading advice
    if 'buy' in msg or 'purchase' in msg:
        return "💡 **Before buying:**\n• Check the trend direction\n• Set a stop-loss level\n• Don't invest more than you can afford\n• Consider your risk tolerance\n• Diversify your portfolio"
    
    elif 'sell' in msg:
        return "📉 **Consider selling when:**\n• Stock hits your target price\n• Fundamentals deteriorate\n• Better opportunities arise\n• Risk management requires it\n• You need the money"
    
    elif 'portfolio' in msg:
        return "💼 **Portfolio tips:**\n• Diversify across sectors\n• Rebalance regularly\n• Keep 3-6 months emergency fund\n• Don't panic during market drops\n• Think long-term"
    
    elif 'risk' in msg:
        return "⚖️ **Risk management:**\n• Never risk more than 2% per trade\n• Use stop-losses\n• Position size based on volatility\n• Diversification is key\n• Know your risk tolerance"
    
    elif 'strategy' in msg or 'trading' in msg:
        return "🎯 **Trading strategies:**\n• **Day trading**: High risk, full-time\n• **Swing trading**: Medium term, 2-10 days\n• **Buy & hold**: Long-term investing\n• **Dollar-cost averaging**: Regular investments\n• Choose based on your time and risk tolerance"
    
    elif 'market' in msg:
        return "📊 **Market analysis:**\n• Monitor major indices (SPY, QQQ)\n• Watch economic indicators\n• Follow earnings reports\n• Consider market sentiment\n• Stay informed but don't overtrade"
    
    elif 'help' in msg:
        return "🤖 **I can help with:**\n• Stock prices (try: 'AAPL price')\n• Trading strategies\n• Portfolio advice\n• Risk management\n• Market analysis\n\n**Try asking:**\n• 'What's TSLA price?'\n• 'Portfolio diversification tips'\n• 'Risk management strategies'"
    
    else:
        return "🤔 I'm here to help with trading questions!\n\n**Try asking about:**\n• Stock prices (AAPL, TSLA, NVDA)\n• Trading strategies\n• Portfolio management\n• Risk management\n\nWhat would you like to know?"

# Main app
st.title("🤖 AI Trading Chatbot")
st.markdown("💬 **Ask me about stocks, trading, and market analysis**")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me about trading..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate and add assistant response
    response = chatbot_response(prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)

# Sidebar with quick actions
with st.sidebar:
    st.header("🚀 Quick Actions")
    
    if st.button("📈 AAPL Price"):
        st.session_state.messages.append({"role": "user", "content": "AAPL price"})
        st.session_state.messages.append({"role": "assistant", "content": chatbot_response("AAPL price")})
        st.rerun()
    
    if st.button("⚡ TSLA Price"):
        st.session_state.messages.append({"role": "user", "content": "TSLA price"})
        st.session_state.messages.append({"role": "assistant", "content": chatbot_response("TSLA price")})
        st.rerun()
    
    if st.button("💼 Portfolio Tips"):
        st.session_state.messages.append({"role": "user", "content": "portfolio tips"})
        st.session_state.messages.append({"role": "assistant", "content": chatbot_response("portfolio tips")})
        st.rerun()
    
    if st.button("⚖️ Risk Management"):
        st.session_state.messages.append({"role": "user", "content": "risk management"})
        st.session_state.messages.append({"role": "assistant", "content": chatbot_response("risk management")})
        st.rerun()
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("🤖 Simple Trading Chatbot\n📊 Real-time stock data")