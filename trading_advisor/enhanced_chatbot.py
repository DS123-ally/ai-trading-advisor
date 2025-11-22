#!/usr/bin/env python3
"""
Enhanced AI Trading Chatbot with Advanced Features
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import json
from datetime import datetime, timedelta
import re

# Page config
st.set_page_config(
    page_title="🤖 AI Trading Assistant",
    page_icon="🚀",
    layout="wide"
)

# Enhanced CSS
st.markdown("""
<style>
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding: 1rem;
        border: 1px solid #ddd;
        border-radius: 10px;
        background: #f8f9fa;
    }
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0 8px auto;
        max-width: 80%;
        text-align: right;
    }
    .bot-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px auto 8px 0;
        max-width: 80%;
    }
    .quick-action {
        background: #e3f2fd;
        border: 1px solid #2196f3;
        border-radius: 20px;
        padding: 8px 16px;
        margin: 4px;
        cursor: pointer;
        display: inline-block;
    }
    .market-alert {
        background: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
    }
    .trading-tip {
        background: #d1ecf1;
        border: 1px solid #17a2b8;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        {
            'type': 'bot',
            'content': "👋 Hello! I'm your AI Trading Assistant. I can help you with:\n\n📊 Real-time stock analysis\n💡 Trading strategies\n📈 Market insights\n⚖️ Risk management\n💼 Portfolio advice\n\nWhat would you like to know?",
            'timestamp': datetime.now()
        }
    ]

if 'user_preferences' not in st.session_state:
    st.session_state.user_preferences = {
        'risk_tolerance': 'Medium',
        'investment_style': 'Balanced',
        'favorite_sectors': ['Technology', 'Healthcare'],
        'watchlist': ['AAPL', 'MSFT', 'GOOGL']
    }

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

def extract_stock_symbols(text):
    """Extract stock symbols from text"""
    # Common patterns for stock symbols
    patterns = [
        r'\b[A-Z]{1,5}\b',  # 1-5 uppercase letters
        r'\$([A-Z]{1,5})',  # $SYMBOL format
    ]
    
    symbols = []
    for pattern in patterns:
        matches = re.findall(pattern, text.upper())
        symbols.extend(matches)
    
    # Filter common words that aren't stock symbols
    common_words = ['THE', 'AND', 'OR', 'BUT', 'FOR', 'WITH', 'TO', 'FROM', 'BY', 'AT', 'IN', 'ON', 'UP', 'DOWN', 'BUY', 'SELL', 'HOLD', 'GET', 'SET', 'PUT', 'CALL', 'ALL', 'ANY', 'CAN', 'MAY', 'WILL', 'NEW', 'OLD', 'TOP', 'LOW', 'HIGH', 'BAD', 'GOOD', 'BIG', 'SMALL']
    
    return [s for s in set(symbols) if s not in common_words and len(s) <= 5]

def get_market_sentiment():
    """Get overall market sentiment"""
    major_indices = ['SPY', 'QQQ', 'DIA']
    sentiment_data = []
    
    for symbol in major_indices:
        data = get_stock_data(symbol)
        if data:
            sentiment_data.append(data['change_percent'])
    
    if sentiment_data:
        avg_change = sum(sentiment_data) / len(sentiment_data)
        if avg_change > 1:
            return "🟢 Bullish", avg_change
        elif avg_change < -1:
            return "🔴 Bearish", avg_change
        else:
            return "🟡 Neutral", avg_change
    
    return "❓ Unknown", 0

def generate_trading_insights(symbol_data):
    """Generate detailed trading insights"""
    if not symbol_data:
        return "Unable to generate insights - no data available"
    
    insights = []
    
    # Price momentum
    if symbol_data['change_percent'] > 5:
        insights.append(f"🚀 Strong bullish momentum (+{symbol_data['change_percent']:.1f}%)")
    elif symbol_data['change_percent'] < -5:
        insights.append(f"📉 Strong bearish pressure ({symbol_data['change_percent']:.1f}%)")
    
    # Volume analysis
    if symbol_data['volume'] > 50000000:
        insights.append("📦 High trading volume indicates strong interest")
    elif symbol_data['volume'] < 10000000:
        insights.append("📦 Low volume - limited market interest")
    
    # Support/Resistance
    support = symbol_data['price'] * 0.95
    resistance = symbol_data['price'] * 1.05
    insights.append(f"📊 Key levels: Support ${support:.2f}, Resistance ${resistance:.2f}")
    
    # Risk assessment
    volatility = abs(symbol_data['change_percent'])
    if volatility > 3:
        insights.append("⚠️ High volatility - increased risk")
    elif volatility < 1:
        insights.append("😴 Low volatility - stable but limited opportunity")
    
    return "\n".join(insights)

def enhanced_ai_response(user_message):
    """Enhanced AI chatbot with advanced features"""
    user_message_lower = user_message.lower()
    
    # Extract stock symbols from message
    symbols = extract_stock_symbols(user_message)
    
    # Stock-specific queries
    if symbols:
        symbol = symbols[0]  # Use first symbol found
        data = get_stock_data(symbol)
        
        if data:
            if 'analysis' in user_message_lower or 'analyze' in user_message_lower:
                insights = generate_trading_insights(data)
                return f"📊 **{symbol} Analysis**\n\n💰 Price: ${data['price']} ({data['change_percent']:+.2f}%)\n📦 Volume: {data['volume']:,}\n📈 Range: ${data['low']} - ${data['high']}\n\n**Insights:**\n{insights}"
            
            elif 'buy' in user_message_lower or 'purchase' in user_message_lower:
                risk_level = st.session_state.user_preferences['risk_tolerance']
                if data['change_percent'] > 0:
                    return f"🟢 **{symbol} Buy Analysis**\n\nCurrent: ${data['price']} (+{data['change_percent']:.2f}%)\n\n✅ Positive momentum\n📊 Consider entry on pullback\n⚖️ Risk level: {risk_level}\n💡 Set stop-loss at ${data['price'] * 0.95:.2f}"
                else:
                    return f"🔴 **{symbol} Buy Analysis**\n\nCurrent: ${data['price']} ({data['change_percent']:.2f}%)\n\n⚠️ Currently declining\n📊 Wait for reversal signals\n💡 Better entry may be available lower"
            
            elif 'sell' in user_message_lower:
                if data['change_percent'] > 3:
                    return f"💰 **{symbol} Sell Analysis**\n\nStrong gains (+{data['change_percent']:.2f}%)\n\n✅ Consider taking profits\n📊 Resistance near ${data['price'] * 1.05:.2f}\n💡 Trail stop-loss to lock gains"
                else:
                    return f"📊 **{symbol} Sell Analysis**\n\nCurrent: ${data['price']} ({data['change_percent']:+.2f}%)\n\n📈 No immediate sell pressure\n⚖️ Hold if fundamentals strong\n💡 Monitor key support levels"
            
            else:
                # General stock info
                trend = "📈 Bullish" if data['change_percent'] > 0 else "📉 Bearish"
                return f"📊 **{symbol} Overview**\n\n💰 ${data['price']} ({data['change_percent']:+.2f}%)\n📦 Volume: {data['volume']:,}\n📈 Day Range: ${data['low']} - ${data['high']}\n🎯 Trend: {trend}\n\n💡 Ask me for detailed analysis, buy/sell recommendations, or technical insights!"
        else:
            return f"❌ Sorry, I couldn't find data for {symbol}. Please check the symbol and try again."
    
    # Market sentiment queries
    elif 'market' in user_message_lower and ('sentiment' in user_message_lower or 'trend' in user_message_lower):
        sentiment, change = get_market_sentiment()
        return f"🌍 **Market Sentiment**: {sentiment}\n\n📊 Major indices average: {change:+.2f}%\n\n💡 Market context helps inform individual stock decisions. {sentiment.split()[1]} markets favor {'growth stocks' if 'Bullish' in sentiment else 'defensive plays' if 'Bearish' in sentiment else 'balanced approach'}."
    
    # Portfolio queries
    elif 'portfolio' in user_message_lower:
        risk_pref = st.session_state.user_preferences['risk_tolerance']
        style = st.session_state.user_preferences['investment_style']
        
        if 'diversification' in user_message_lower or 'diversify' in user_message_lower:
            return f"💼 **Portfolio Diversification Tips**\n\n🎯 Your profile: {risk_pref} risk, {style} style\n\n✅ **Recommended allocation:**\n• 60% Stocks (mix of growth/value)\n• 30% Bonds/Fixed income\n• 10% Alternative investments\n\n🏢 **Sector diversification:**\n• Technology: 20-25%\n• Healthcare: 15-20%\n• Financials: 10-15%\n• Consumer goods: 10-15%\n• Others: 30-40%\n\n💡 Rebalance quarterly!"
        
        elif 'rebalance' in user_message_lower:
            return f"⚖️ **Portfolio Rebalancing Guide**\n\n📅 **When to rebalance:**\n• Quarterly or semi-annually\n• When allocation drifts >5% from target\n• After major market moves\n\n🔄 **How to rebalance:**\n1. Review current allocation\n2. Compare to target allocation\n3. Sell overweight positions\n4. Buy underweight positions\n5. Consider tax implications\n\n💡 Use new contributions to rebalance when possible!"
        
        else:
            return f"💼 **Portfolio Management**\n\n🎯 Your preferences: {risk_pref} risk tolerance\n\n✅ **Key principles:**\n• Diversification across sectors\n• Regular rebalancing\n• Long-term perspective\n• Risk management\n\n📊 **Current focus sectors:** {', '.join(st.session_state.user_preferences['favorite_sectors'])}\n\n💡 Ask about diversification, rebalancing, or specific allocation strategies!"
    
    # Risk management
    elif 'risk' in user_message_lower:
        if 'management' in user_message_lower or 'manage' in user_message_lower:
            return f"⚖️ **Risk Management Essentials**\n\n🎯 **Position sizing:**\n• Never risk >2% of portfolio per trade\n• Use position size = (Account × Risk%) ÷ Stop distance\n\n🛑 **Stop losses:**\n• Set before entering trade\n• Technical: Below support levels\n• Percentage: 5-10% for stocks\n\n📊 **Diversification:**\n• Max 5% in any single stock\n• Spread across sectors\n• Consider correlation\n\n💡 Risk management is more important than picking winners!"
        
        elif 'tolerance' in user_message_lower:
            current_tolerance = st.session_state.user_preferences['risk_tolerance']
            return f"📊 **Risk Tolerance Assessment**\n\nCurrent setting: {current_tolerance}\n\n🔴 **Conservative:** Preserve capital, low volatility\n🟡 **Moderate:** Balanced growth/safety\n🟢 **Aggressive:** Maximum growth, high volatility\n\n💡 Your risk tolerance should match:\n• Investment timeline\n• Financial situation\n• Emotional comfort\n• Experience level\n\nWant to update your risk profile?"
    
    # Trading strategies
    elif 'strategy' in user_message_lower or 'strategies' in user_message_lower:
        if 'day trading' in user_message_lower or 'daytrading' in user_message_lower:
            return f"⚡ **Day Trading Strategy**\n\n⏰ **Time commitment:** Full-time focus required\n💰 **Capital:** $25K minimum (PDT rule)\n📊 **Tools needed:** Level 2 data, fast execution\n\n🎯 **Key strategies:**\n• Momentum trading\n• Scalping\n• Gap trading\n• News-based trading\n\n⚠️ **Risks:** High stress, significant losses possible\n💡 Practice with paper trading first!"
        
        elif 'swing' in user_message_lower:
            return f"📈 **Swing Trading Strategy**\n\n⏰ **Timeframe:** 2-10 days per trade\n📊 **Analysis:** Technical patterns, support/resistance\n🎯 **Targets:** 5-15% moves\n\n✅ **Advantages:**\n• Less time intensive than day trading\n• Captures medium-term trends\n• Lower transaction costs\n\n📋 **Setup process:**\n1. Identify trend direction\n2. Find entry at support/resistance\n3. Set stop loss and profit targets\n4. Monitor and adjust\n\n💡 Perfect for part-time traders!"
        
        else:
            return f"🎯 **Trading Strategies Overview**\n\n📊 **By timeframe:**\n• Day trading: Minutes to hours\n• Swing trading: Days to weeks\n• Position trading: Weeks to months\n• Investing: Months to years\n\n🔍 **By analysis type:**\n• Technical analysis\n• Fundamental analysis\n• Quantitative strategies\n• Sentiment-based trading\n\n💡 Choose strategy based on your time, capital, and risk tolerance!"
    
    # Technical analysis
    elif 'technical' in user_message_lower or 'chart' in user_message_lower:
        return f"📊 **Technical Analysis Basics**\n\n🕯️ **Key patterns:**\n• Support/Resistance levels\n• Trend lines and channels\n• Candlestick patterns\n• Chart formations\n\n📈 **Popular indicators:**\n• Moving averages (SMA, EMA)\n• RSI (overbought/oversold)\n• MACD (momentum)\n• Volume analysis\n\n🎯 **Trading signals:**\n• Breakouts from patterns\n• Moving average crossovers\n• Divergences\n• Volume confirmation\n\n💡 Combine multiple indicators for better accuracy!"
    
    # Options trading
    elif 'option' in user_message_lower or 'options' in user_message_lower:
        return f"📋 **Options Trading Basics**\n\n🎯 **Call options:** Right to buy at strike price\n🎯 **Put options:** Right to sell at strike price\n\n✅ **Basic strategies:**\n• Buy calls: Bullish, limited risk\n• Buy puts: Bearish, limited risk\n• Covered calls: Income generation\n• Cash-secured puts: Acquire stocks\n\n⚠️ **Key risks:**\n• Time decay (theta)\n• Volatility changes\n• Complexity\n• Potential total loss\n\n💡 Start with buying options, learn Greeks, practice with paper trading!"
    
    # Crypto queries
    elif 'crypto' in user_message_lower or 'bitcoin' in user_message_lower or 'ethereum' in user_message_lower:
        return f"₿ **Cryptocurrency Trading**\n\n🎯 **Major cryptocurrencies:**\n• Bitcoin (BTC): Digital gold\n• Ethereum (ETH): Smart contracts\n• Others: Diverse use cases\n\n⚠️ **Key considerations:**\n• Extreme volatility\n• 24/7 markets\n• Regulatory uncertainty\n• Technology risks\n\n💡 **If trading crypto:**\n• Start small (1-5% of portfolio)\n• Use reputable exchanges\n• Secure storage (hardware wallets)\n• Understand the technology\n\n📊 Treat as high-risk speculation!"
    
    # General help
    elif 'help' in user_message_lower:
        return f"🤖 **AI Trading Assistant Help**\n\n💬 **What I can help with:**\n\n📊 **Stock Analysis:**\n• Real-time prices and data\n• Technical analysis\n• Buy/sell recommendations\n• Risk assessment\n\n💼 **Portfolio Management:**\n• Diversification strategies\n• Risk management\n• Rebalancing advice\n• Asset allocation\n\n🎯 **Trading Strategies:**\n• Day trading, swing trading\n• Technical analysis\n• Options basics\n• Market sentiment\n\n💡 **Tips:**\n• Mention stock symbols (AAPL, TSLA)\n• Ask specific questions\n• Use keywords like 'analyze', 'buy', 'risk'\n• Try quick actions below!"
    
    # Default response with suggestions
    else:
        return f"🤔 I'd love to help! Here are some things you can ask me:\n\n📊 **Stock queries:**\n• \"Analyze AAPL\"\n• \"Should I buy TSLA?\"\n• \"NVDA technical analysis\"\n\n💼 **Portfolio help:**\n• \"Portfolio diversification tips\"\n• \"Risk management strategies\"\n• \"How to rebalance portfolio\"\n\n🎯 **Trading strategies:**\n• \"Day trading strategies\"\n• \"Technical analysis basics\"\n• \"Options trading guide\"\n\n💡 Try the quick action buttons below or ask about any stock symbol!"

# Main app
st.title("🤖 Enhanced AI Trading Assistant")
st.markdown("💬 **Your intelligent trading companion with advanced market insights**")

# User preferences sidebar
with st.sidebar:
    st.header("⚙️ Preferences")
    
    risk_tolerance = st.selectbox(
        "Risk Tolerance",
        ["Conservative", "Moderate", "Aggressive"],
        index=["Conservative", "Moderate", "Aggressive"].index(st.session_state.user_preferences['risk_tolerance'])
    )
    
    investment_style = st.selectbox(
        "Investment Style",
        ["Growth", "Value", "Balanced", "Income"],
        index=["Growth", "Value", "Balanced", "Income"].index(st.session_state.user_preferences['investment_style'])
    )
    
    favorite_sectors = st.multiselect(
        "Favorite Sectors",
        ["Technology", "Healthcare", "Finance", "Energy", "Consumer", "Industrial"],
        default=st.session_state.user_preferences['favorite_sectors']
    )
    
    # Update preferences
    st.session_state.user_preferences.update({
        'risk_tolerance': risk_tolerance,
        'investment_style': investment_style,
        'favorite_sectors': favorite_sectors
    })
    
    st.markdown("---")
    
    # Market overview
    st.subheader("📊 Market Pulse")
    sentiment, change = get_market_sentiment()
    st.markdown(f"**Sentiment:** {sentiment}")
    st.markdown(f"**Change:** {change:+.2f}%")

# Chat interface
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("💬 Chat Interface")
    
    # Chat history container
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.chat_history:
            if message['type'] == 'user':
                st.markdown(f'<div class="user-message">👤 {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bot-message">🤖 {message["content"]}</div>', unsafe_allow_html=True)
    
    # Chat input
    user_input = st.text_input("💬 Ask me anything about trading:", key="chat_input", placeholder="e.g., 'Analyze AAPL' or 'Portfolio diversification tips'")
    
    col_send, col_clear = st.columns([1, 1])
    
    with col_send:
        if st.button("📤 Send", use_container_width=True) and user_input:
            # Add user message
            st.session_state.chat_history.append({
                'type': 'user',
                'content': user_input,
                'timestamp': datetime.now()
            })
            
            # Generate AI response
            ai_response = enhanced_ai_response(user_input)
            
            # Add AI response
            st.session_state.chat_history.append({
                'type': 'bot',
                'content': ai_response,
                'timestamp': datetime.now()
            })
            
            st.rerun()
    
    with col_clear:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = [st.session_state.chat_history[0]]  # Keep welcome message
            st.rerun()

with col2:
    st.subheader("🚀 Quick Actions")
    
    # Stock analysis buttons
    st.markdown("**📊 Stock Analysis**")
    
    popular_stocks = ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'GOOGL', 'AMZN']
    
    for stock in popular_stocks:
        if st.button(f"📈 Analyze {stock}", key=f"analyze_{stock}", use_container_width=True):
            st.session_state.chat_history.append({
                'type': 'user',
                'content': f'Analyze {stock}',
                'timestamp': datetime.now()
            })
            st.session_state.chat_history.append({
                'type': 'bot',
                'content': enhanced_ai_response(f'analyze {stock}'),
                'timestamp': datetime.now()
            })
            st.rerun()
    
    st.markdown("---")
    st.markdown("**💡 Quick Topics**")
    
    quick_topics = [
        ("📊 Market Sentiment", "market sentiment"),
        ("💼 Portfolio Tips", "portfolio management"),
        ("⚖️ Risk Management", "risk management"),
        ("🎯 Trading Strategies", "trading strategies"),
        ("📈 Technical Analysis", "technical analysis"),
        ("📋 Options Basics", "options trading")
    ]
    
    for topic_name, topic_query in quick_topics:
        if st.button(topic_name, key=f"topic_{topic_query}", use_container_width=True):
            st.session_state.chat_history.append({
                'type': 'user',
                'content': topic_query,
                'timestamp': datetime.now()
            })
            st.session_state.chat_history.append({
                'type': 'bot',
                'content': enhanced_ai_response(topic_query),
                'timestamp': datetime.now()
            })
            st.rerun()

# Market alerts section
st.markdown("---")
st.subheader("🚨 Smart Market Alerts")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="market-alert">📈 <strong>Momentum Alert</strong><br>NVDA up 4.2% on AI news</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="trading-tip">💡 <strong>Trading Tip</strong><br>Consider profit-taking on overextended positions</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="market-alert">⚠️ <strong>Risk Alert</strong><br>VIX elevated - increased volatility expected</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("🤖 **Enhanced AI Trading Assistant** | 📊 Real-time insights | 💡 Personalized advice")