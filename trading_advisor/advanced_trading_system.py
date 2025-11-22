#!/usr/bin/env python3
"""
Advanced Trading System with Candlestick Patterns, Trend Analysis & Trading Plans
Run: streamlit run advanced_trading_system.py
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta
import talib
import warnings
warnings.filterwarnings('ignore')

# Page config
st.set_page_config(
    page_title="🎯 Advanced Trading System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .pattern-bullish { background: linear-gradient(90deg, #00ff00, #32cd32); padding: 10px; border-radius: 5px; color: black; font-weight: bold; }
    .pattern-bearish { background: linear-gradient(90deg, #ff0000, #ff6347); padding: 10px; border-radius: 5px; color: white; font-weight: bold; }
    .pattern-neutral { background: linear-gradient(90deg, #ffa500, #ffd700); padding: 10px; border-radius: 5px; color: black; font-weight: bold; }
    .trend-up { color: #00ff00; font-size: 24px; }
    .trend-down { color: #ff0000; font-size: 24px; }
    .trend-sideways { color: #ffa500; font-size: 24px; }
    .entry-level { background: #e6ffe6; padding: 8px; border-left: 4px solid #00ff00; margin: 5px 0; }
    .exit-level { background: #ffe6e6; padding: 8px; border-left: 4px solid #ff0000; margin: 5px 0; }
    .stop-level { background: #fff0e6; padding: 8px; border-left: 4px solid #ffa500; margin: 5px 0; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']

# Sidebar
st.sidebar.title("🎯 Advanced Trading System")
st.sidebar.markdown("---")

# Navigation
page = st.sidebar.selectbox("📊 Navigate", [
    "🕯️ Candlestick Patterns", 
    "📈 Trend Analysis", 
    "🎯 Entry/Exit Levels",
    "📋 Daily Trading Plan",
    "🔍 Pattern Scanner"
])

# Stock selection
selected_symbol = st.sidebar.selectbox("Select Stock", st.session_state.watchlist)
timeframe = st.sidebar.selectbox("Timeframe", ["1d", "5d", "1mo", "3mo", "6mo", "1y"])

# Helper functions
@st.cache_data(ttl=300)
def get_stock_data(symbol, period="3mo"):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        return hist
    except:
        return pd.DataFrame()

def identify_candlestick_patterns(data):
    """Identify major candlestick patterns"""
    patterns = {}
    
    if len(data) < 10:
        return patterns
    
    try:
        # Single candlestick patterns
        patterns['Doji'] = talib.CDLDOJI(data['Open'], data['High'], data['Low'], data['Close'])
        patterns['Hammer'] = talib.CDLHAMMER(data['Open'], data['High'], data['Low'], data['Close'])
        patterns['Hanging Man'] = talib.CDLHANGINGMAN(data['Open'], data['High'], data['Low'], data['Close'])
        patterns['Shooting Star'] = talib.CDLSHOOTINGSTAR(data['Open'], data['High'], data['Low'], data['Close'])
        patterns['Marubozu'] = talib.CDLMARUBOZU(data['Open'], data['High'], data['Low'], data['Close'])
        
        # Multi-candlestick patterns
        patterns['Engulfing'] = talib.CDLENGULFING(data['Open'], data['High'], data['Low'], data['Close'])
        patterns['Harami'] = talib.CDLHARAMI(data['Open'], data['High'], data['Low'], data['Close'])
        patterns['Morning Star'] = talib.CDLMORNINGSTAR(data['Open'], data['High'], data['Low'], data['Close'])
        patterns['Evening Star'] = talib.CDLEVENINGSTAR(data['Open'], data['High'], data['Low'], data['Close'])
        patterns['Three White Soldiers'] = talib.CDL3WHITESOLDIERS(data['Open'], data['High'], data['Low'], data['Close'])
        patterns['Three Black Crows'] = talib.CDL3BLACKCROWS(data['Open'], data['High'], data['Low'], data['Close'])
        
    except Exception as e:
        st.error(f"Error calculating patterns: {e}")
    
    return patterns

def analyze_trend(data):
    """Analyze current trend using multiple indicators"""
    if len(data) < 50:
        return "Insufficient Data", 0
    
    # Moving averages
    sma_20 = data['Close'].rolling(20).mean().iloc[-1]
    sma_50 = data['Close'].rolling(50).mean().iloc[-1]
    current_price = data['Close'].iloc[-1]
    
    # ADX for trend strength
    try:
        adx = talib.ADX(data['High'], data['Low'], data['Close'], timeperiod=14).iloc[-1]
    except:
        adx = 25
    
    # Trend determination
    if current_price > sma_20 > sma_50:
        trend = "Uptrend"
        strength = min(adx, 100)
    elif current_price < sma_20 < sma_50:
        trend = "Downtrend" 
        strength = min(adx, 100)
    else:
        trend = "Sideways"
        strength = max(25 - adx, 0) if adx > 25 else 25
    
    return trend, strength

def calculate_support_resistance(data):
    """Calculate support and resistance levels"""
    if len(data) < 20:
        return [], []
    
    # Pivot points
    highs = data['High'].rolling(window=5, center=True).max()
    lows = data['Low'].rolling(window=5, center=True).min()
    
    resistance_levels = []
    support_levels = []
    
    for i in range(2, len(data)-2):
        # Resistance (local highs)
        if data['High'].iloc[i] == highs.iloc[i]:
            resistance_levels.append(data['High'].iloc[i])
        
        # Support (local lows)
        if data['Low'].iloc[i] == lows.iloc[i]:
            support_levels.append(data['Low'].iloc[i])
    
    # Remove duplicates and sort
    resistance_levels = sorted(list(set(resistance_levels)), reverse=True)[:5]
    support_levels = sorted(list(set(support_levels)))[:5]
    
    return support_levels, resistance_levels

def generate_entry_exit_levels(data, trend):
    """Generate entry and exit levels based on technical analysis"""
    current_price = data['Close'].iloc[-1]
    
    # Calculate ATR for stop loss
    try:
        atr = talib.ATR(data['High'], data['Low'], data['Close'], timeperiod=14).iloc[-1]
    except:
        atr = current_price * 0.02  # 2% fallback
    
    support_levels, resistance_levels = calculate_support_resistance(data)
    
    levels = {}
    
    if trend == "Uptrend":
        # Long position levels
        entry_price = current_price
        stop_loss = current_price - (2 * atr)
        take_profit_1 = current_price + (2 * atr)
        take_profit_2 = current_price + (4 * atr)
        
        # Use nearest resistance as target if available
        if resistance_levels:
            nearest_resistance = min([r for r in resistance_levels if r > current_price], default=take_profit_1)
            take_profit_1 = min(take_profit_1, nearest_resistance)
        
        levels = {
            'direction': 'LONG',
            'entry': entry_price,
            'stop_loss': stop_loss,
            'take_profit_1': take_profit_1,
            'take_profit_2': take_profit_2,
            'risk_reward': (take_profit_1 - entry_price) / (entry_price - stop_loss)
        }
        
    elif trend == "Downtrend":
        # Short position levels
        entry_price = current_price
        stop_loss = current_price + (2 * atr)
        take_profit_1 = current_price - (2 * atr)
        take_profit_2 = current_price - (4 * atr)
        
        # Use nearest support as target if available
        if support_levels:
            nearest_support = max([s for s in support_levels if s < current_price], default=take_profit_1)
            take_profit_1 = max(take_profit_1, nearest_support)
        
        levels = {
            'direction': 'SHORT',
            'entry': entry_price,
            'stop_loss': stop_loss,
            'take_profit_1': take_profit_1,
            'take_profit_2': take_profit_2,
            'risk_reward': (entry_price - take_profit_1) / (stop_loss - entry_price)
        }
    
    else:
        levels = {
            'direction': 'WAIT',
            'message': 'No clear trend - wait for breakout'
        }
    
    return levels

def create_trading_plan(symbol, data, patterns, trend, levels):
    """Generate comprehensive daily trading plan"""
    current_price = data['Close'].iloc[-1]
    volume = data['Volume'].iloc[-1]
    
    # Recent patterns
    recent_patterns = []
    for pattern_name, pattern_data in patterns.items():
        if len(pattern_data) > 0 and pattern_data.iloc[-1] != 0:
            signal_type = "Bullish" if pattern_data.iloc[-1] > 0 else "Bearish"
            recent_patterns.append(f"{pattern_name} ({signal_type})")
    
    plan = {
        'symbol': symbol,
        'date': datetime.now().strftime('%Y-%m-%d'),
        'current_price': current_price,
        'volume': volume,
        'trend': trend,
        'patterns': recent_patterns,
        'levels': levels,
        'market_context': analyze_market_context(data),
        'risk_management': calculate_risk_management(current_price, levels),
        'action_plan': generate_action_plan(trend, recent_patterns, levels)
    }
    
    return plan

def analyze_market_context(data):
    """Analyze broader market context"""
    # Volatility
    returns = data['Close'].pct_change().dropna()
    volatility = returns.std() * np.sqrt(252) * 100  # Annualized volatility
    
    # Volume trend
    avg_volume = data['Volume'].rolling(20).mean().iloc[-1]
    current_volume = data['Volume'].iloc[-1]
    volume_ratio = current_volume / avg_volume
    
    context = {
        'volatility': f"{volatility:.1f}%",
        'volume_status': 'High' if volume_ratio > 1.5 else 'Normal' if volume_ratio > 0.5 else 'Low',
        'volume_ratio': f"{volume_ratio:.1f}x"
    }
    
    return context

def calculate_risk_management(current_price, levels):
    """Calculate position sizing and risk metrics"""
    if levels.get('direction') == 'WAIT':
        return {'message': 'No position recommended'}
    
    account_size = 10000  # Default account size
    risk_per_trade = 0.02  # 2% risk per trade
    
    if 'stop_loss' in levels:
        risk_per_share = abs(current_price - levels['stop_loss'])
        position_size = (account_size * risk_per_trade) / risk_per_share
        max_shares = int(position_size)
        
        return {
            'account_size': account_size,
            'risk_per_trade': f"{risk_per_trade:.1%}",
            'risk_per_share': f"${risk_per_share:.2f}",
            'max_position_size': max_shares,
            'total_risk': f"${max_shares * risk_per_share:.2f}"
        }
    
    return {'message': 'Risk calculation unavailable'}

def generate_action_plan(trend, patterns, levels):
    """Generate specific action plan"""
    actions = []
    
    if trend == "Uptrend":
        actions.append("✅ Look for long opportunities on pullbacks")
        actions.append("📈 Monitor for continuation patterns")
        
    elif trend == "Downtrend":
        actions.append("🔻 Consider short positions on rallies")
        actions.append("📉 Watch for reversal signals")
        
    else:
        actions.append("⏳ Wait for clear directional breakout")
        actions.append("👀 Monitor key support/resistance levels")
    
    if patterns:
        actions.append(f"🕯️ Recent patterns: {', '.join(patterns[:2])}")
    
    if levels.get('direction') != 'WAIT':
        actions.append(f"🎯 Entry: ${levels['entry']:.2f}")
        actions.append(f"🛑 Stop: ${levels['stop_loss']:.2f}")
        actions.append(f"💰 Target: ${levels['take_profit_1']:.2f}")
    
    return actions

# Main content based on selected page
if page == "🕯️ Candlestick Patterns":
    st.title("🕯️ Candlestick Pattern Analysis")
    
    data = get_stock_data(selected_symbol, timeframe)
    
    if not data.empty:
        # Chart with patterns
        fig = go.Figure()
        
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name=selected_symbol
        ))
        
        fig.update_layout(
            title=f"{selected_symbol} Candlestick Chart",
            template="plotly_dark",
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Pattern identification
        st.subheader("🔍 Detected Patterns")
        
        patterns = identify_candlestick_patterns(data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Recent Patterns (Last 5 Days):**")
            recent_patterns_found = False
            
            for pattern_name, pattern_data in patterns.items():
                if len(pattern_data) > 0:
                    recent_signals = pattern_data.tail(5)
                    if recent_signals.abs().sum() > 0:
                        recent_patterns_found = True
                        for i, signal in enumerate(recent_signals):
                            if signal != 0:
                                date = recent_signals.index[i].strftime('%Y-%m-%d')
                                signal_type = "Bullish" if signal > 0 else "Bearish"
                                pattern_class = "pattern-bullish" if signal > 0 else "pattern-bearish"
                                st.markdown(f'<div class="{pattern_class}">{pattern_name} - {signal_type} ({date})</div>', unsafe_allow_html=True)
            
            if not recent_patterns_found:
                st.info("No significant patterns detected in recent days")
        
        with col2:
            st.write("**Pattern Explanations:**")
            
            pattern_explanations = {
                'Doji': 'Indecision - potential reversal signal',
                'Hammer': 'Bullish reversal after downtrend',
                'Hanging Man': 'Bearish reversal after uptrend',
                'Shooting Star': 'Bearish reversal signal',
                'Engulfing': 'Strong reversal pattern',
                'Morning Star': 'Bullish reversal (3-candle)',
                'Evening Star': 'Bearish reversal (3-candle)',
                'Three White Soldiers': 'Strong bullish continuation',
                'Three Black Crows': 'Strong bearish continuation'
            }
            
            for pattern, explanation in pattern_explanations.items():
                st.write(f"**{pattern}:** {explanation}")

elif page == "📈 Trend Analysis":
    st.title("📈 Comprehensive Trend Analysis")
    
    data = get_stock_data(selected_symbol, timeframe)
    
    if not data.empty:
        trend, strength = analyze_trend(data)
        
        # Trend display
        col1, col2, col3 = st.columns(3)
        
        with col1:
            trend_icon = "📈" if trend == "Uptrend" else "📉" if trend == "Downtrend" else "➡️"
            trend_class = "trend-up" if trend == "Uptrend" else "trend-down" if trend == "Downtrend" else "trend-sideways"
            st.markdown(f'<div class="{trend_class}">{trend_icon} {trend}</div>', unsafe_allow_html=True)
        
        with col2:
            st.metric("Trend Strength", f"{strength:.1f}/100")
        
        with col3:
            current_price = data['Close'].iloc[-1]
            st.metric("Current Price", f"${current_price:.2f}")
        
        # Trend analysis chart
        fig = go.Figure()
        
        # Price and moving averages
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Price', line=dict(color='white', width=2)))
        
        sma_20 = data['Close'].rolling(20).mean()
        sma_50 = data['Close'].rolling(50).mean()
        
        fig.add_trace(go.Scatter(x=data.index, y=sma_20, name='SMA 20', line=dict(color='orange', width=1)))
        fig.add_trace(go.Scatter(x=data.index, y=sma_50, name='SMA 50', line=dict(color='blue', width=1)))
        
        fig.update_layout(
            title=f"{selected_symbol} Trend Analysis",
            template="plotly_dark",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Trend details
        st.subheader("📊 Trend Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Technical Indicators:**")
            st.write(f"• 20-day SMA: ${sma_20.iloc[-1]:.2f}")
            st.write(f"• 50-day SMA: ${sma_50.iloc[-1]:.2f}")
            st.write(f"• Price vs SMA20: {((current_price/sma_20.iloc[-1]-1)*100):+.1f}%")
            st.write(f"• Price vs SMA50: {((current_price/sma_50.iloc[-1]-1)*100):+.1f}%")
        
        with col2:
            st.write("**Trend Interpretation:**")
            if trend == "Uptrend":
                st.success("🟢 Strong upward momentum. Look for buying opportunities on pullbacks.")
            elif trend == "Downtrend":
                st.error("🔴 Bearish trend in place. Consider short positions or wait for reversal.")
            else:
                st.warning("🟡 Sideways movement. Wait for clear breakout direction.")

elif page == "🎯 Entry/Exit Levels":
    st.title("🎯 Entry & Exit Level Analysis")
    
    data = get_stock_data(selected_symbol, timeframe)
    
    if not data.empty:
        trend, _ = analyze_trend(data)
        levels = generate_entry_exit_levels(data, trend)
        support_levels, resistance_levels = calculate_support_resistance(data)
        
        # Chart with levels
        fig = go.Figure()
        
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name=selected_symbol
        ))
        
        # Add support and resistance lines
        for support in support_levels:
            fig.add_hline(y=support, line_dash="dash", line_color="green", annotation_text=f"Support: ${support:.2f}")
        
        for resistance in resistance_levels:
            fig.add_hline(y=resistance, line_dash="dash", line_color="red", annotation_text=f"Resistance: ${resistance:.2f}")
        
        # Add entry/exit levels if available
        if levels.get('direction') != 'WAIT':
            fig.add_hline(y=levels['entry'], line_color="blue", annotation_text=f"Entry: ${levels['entry']:.2f}")
            fig.add_hline(y=levels['stop_loss'], line_color="orange", annotation_text=f"Stop: ${levels['stop_loss']:.2f}")
            fig.add_hline(y=levels['take_profit_1'], line_color="purple", annotation_text=f"Target: ${levels['take_profit_1']:.2f}")
        
        fig.update_layout(
            title=f"{selected_symbol} Entry/Exit Levels",
            template="plotly_dark",
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Level details
        st.subheader("📋 Trading Levels")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Support & Resistance:**")
            
            if support_levels:
                st.write("🟢 **Support Levels:**")
                for i, level in enumerate(support_levels):
                    st.write(f"  S{i+1}: ${level:.2f}")
            
            if resistance_levels:
                st.write("🔴 **Resistance Levels:**")
                for i, level in enumerate(resistance_levels):
                    st.write(f"  R{i+1}: ${level:.2f}")
        
        with col2:
            st.write("**Trading Setup:**")
            
            if levels.get('direction') != 'WAIT':
                direction_color = "🟢" if levels['direction'] == 'LONG' else "🔴"
                st.markdown(f'<div class="entry-level">{direction_color} <strong>Direction:</strong> {levels["direction"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="entry-level">🎯 <strong>Entry:</strong> ${levels["entry"]:.2f}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="stop-level">🛑 <strong>Stop Loss:</strong> ${levels["stop_loss"]:.2f}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="exit-level">💰 <strong>Take Profit:</strong> ${levels["take_profit_1"]:.2f}</div>', unsafe_allow_html=True)
                
                if 'risk_reward' in levels:
                    st.write(f"⚖️ **Risk/Reward Ratio:** {levels['risk_reward']:.2f}")
            else:
                st.info("⏳ No clear setup - wait for better opportunity")

elif page == "📋 Daily Trading Plan":
    st.title("📋 Daily Trading Plan")
    
    data = get_stock_data(selected_symbol, timeframe)
    
    if not data.empty:
        patterns = identify_candlestick_patterns(data)
        trend, _ = analyze_trend(data)
        levels = generate_entry_exit_levels(data, trend)
        
        # Generate comprehensive trading plan
        plan = create_trading_plan(selected_symbol, data, patterns, trend, levels)
        
        # Display trading plan
        st.subheader(f"📊 Trading Plan for {plan['symbol']} - {plan['date']}")
        
        # Market overview
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Current Price", f"${plan['current_price']:.2f}")
        
        with col2:
            trend_icon = "📈" if plan['trend'] == "Uptrend" else "📉" if plan['trend'] == "Downtrend" else "➡️"
            st.metric("Trend", f"{trend_icon} {plan['trend']}")
        
        with col3:
            st.metric("Volume", f"{plan['volume']:,}")
        
        with col4:
            st.metric("Volatility", plan['market_context']['volatility'])
        
        # Action plan
        st.subheader("🎯 Action Plan")
        
        for action in plan['action_plan']:
            st.write(f"• {action}")
        
        # Risk management
        st.subheader("⚖️ Risk Management")
        
        risk_mgmt = plan['risk_management']
        if 'message' not in risk_mgmt:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"💰 **Account Size:** ${risk_mgmt['account_size']:,}")
                st.write(f"📊 **Risk Per Trade:** {risk_mgmt['risk_per_trade']}")
                st.write(f"💸 **Risk Per Share:** {risk_mgmt['risk_per_share']}")
            
            with col2:
                st.write(f"📈 **Max Position:** {risk_mgmt['max_position_size']} shares")
                st.write(f"🎯 **Total Risk:** {risk_mgmt['total_risk']}")
        else:
            st.info(risk_mgmt['message'])
        
        # Pattern summary
        if plan['patterns']:
            st.subheader("🕯️ Recent Patterns")
            for pattern in plan['patterns']:
                pattern_class = "pattern-bullish" if "Bullish" in pattern else "pattern-bearish"
                st.markdown(f'<div class="{pattern_class}">{pattern}</div>', unsafe_allow_html=True)

elif page == "🔍 Pattern Scanner":
    st.title("🔍 Multi-Stock Pattern Scanner")
    
    # Scan multiple stocks
    scan_symbols = st.multiselect(
        "Select stocks to scan",
        ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'AMZN', 'META', 'NFLX', 'AMD', 'CRM'],
        default=['AAPL', 'MSFT', 'GOOGL', 'TSLA']
    )
    
    if st.button("🔍 Scan for Patterns") and scan_symbols:
        results = []
        
        progress_bar = st.progress(0)
        
        for i, symbol in enumerate(scan_symbols):
            data = get_stock_data(symbol, "1mo")
            
            if not data.empty:
                patterns = identify_candlestick_patterns(data)
                trend, strength = analyze_trend(data)
                
                # Check for recent patterns
                recent_patterns = []
                for pattern_name, pattern_data in patterns.items():
                    if len(pattern_data) > 0 and pattern_data.tail(3).abs().sum() > 0:
                        recent_patterns.append(pattern_name)
                
                if recent_patterns:
                    results.append({
                        'Symbol': symbol,
                        'Price': f"${data['Close'].iloc[-1]:.2f}",
                        'Trend': trend,
                        'Strength': f"{strength:.0f}",
                        'Patterns': ', '.join(recent_patterns[:2])
                    })
            
            progress_bar.progress((i + 1) / len(scan_symbols))
        
        # Display results
        if results:
            st.subheader(f"📊 Scan Results ({len(results)} stocks with patterns)")
            df = pd.DataFrame(results)
            st.dataframe(df, hide_index=True, use_container_width=True)
        else:
            st.info("No significant patterns found in selected stocks")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("🎯 Advanced Trading System\n📊 Professional Pattern Analysis")

# Auto-refresh option
if st.sidebar.checkbox("🔄 Auto-refresh (60s)"):
    import time
    time.sleep(60)
    st.experimental_rerun()