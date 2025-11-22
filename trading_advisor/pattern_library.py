"""
Candlestick Pattern Library - Educational Reference
"""

CANDLESTICK_PATTERNS = {
    "Single Candle Patterns": {
        "Doji": {
            "description": "Open and close prices are nearly equal, indicating indecision",
            "signal": "Reversal (context dependent)",
            "reliability": "Medium",
            "formation": "Small body with long upper and lower shadows"
        },
        "Hammer": {
            "description": "Bullish reversal pattern after downtrend",
            "signal": "Bullish reversal",
            "reliability": "High",
            "formation": "Small body at top, long lower shadow, little/no upper shadow"
        },
        "Hanging Man": {
            "description": "Bearish reversal pattern after uptrend",
            "signal": "Bearish reversal",
            "reliability": "Medium",
            "formation": "Small body at top, long lower shadow (same as hammer but different context)"
        },
        "Shooting Star": {
            "description": "Bearish reversal pattern after uptrend",
            "signal": "Bearish reversal",
            "reliability": "High",
            "formation": "Small body at bottom, long upper shadow, little/no lower shadow"
        },
        "Marubozu": {
            "description": "Strong directional movement with no shadows",
            "signal": "Continuation",
            "reliability": "High",
            "formation": "Large body with no upper or lower shadows"
        }
    },
    
    "Two Candle Patterns": {
        "Bullish Engulfing": {
            "description": "Large bullish candle completely engulfs previous bearish candle",
            "signal": "Bullish reversal",
            "reliability": "High",
            "formation": "Small red candle followed by large green candle that engulfs it"
        },
        "Bearish Engulfing": {
            "description": "Large bearish candle completely engulfs previous bullish candle",
            "signal": "Bearish reversal",
            "reliability": "High",
            "formation": "Small green candle followed by large red candle that engulfs it"
        },
        "Bullish Harami": {
            "description": "Small bullish candle within body of previous large bearish candle",
            "signal": "Bullish reversal",
            "reliability": "Medium",
            "formation": "Large red candle followed by small green candle within its body"
        },
        "Bearish Harami": {
            "description": "Small bearish candle within body of previous large bullish candle",
            "signal": "Bearish reversal",
            "reliability": "Medium",
            "formation": "Large green candle followed by small red candle within its body"
        }
    },
    
    "Three Candle Patterns": {
        "Morning Star": {
            "description": "Three-candle bullish reversal pattern",
            "signal": "Bullish reversal",
            "reliability": "Very High",
            "formation": "Large red candle, small-bodied candle (gap down), large green candle (gap up)"
        },
        "Evening Star": {
            "description": "Three-candle bearish reversal pattern",
            "signal": "Bearish reversal",
            "reliability": "Very High",
            "formation": "Large green candle, small-bodied candle (gap up), large red candle (gap down)"
        },
        "Three White Soldiers": {
            "description": "Three consecutive long bullish candles",
            "signal": "Strong bullish continuation",
            "reliability": "High",
            "formation": "Three consecutive large green candles with higher opens and closes"
        },
        "Three Black Crows": {
            "description": "Three consecutive long bearish candles",
            "signal": "Strong bearish continuation",
            "reliability": "High",
            "formation": "Three consecutive large red candles with lower opens and closes"
        }
    }
}

TREND_ANALYSIS_GUIDE = {
    "Uptrend Characteristics": [
        "Price above 20-day and 50-day moving averages",
        "Moving averages sloping upward",
        "Higher highs and higher lows pattern",
        "Strong volume on up moves",
        "ADX above 25 with +DI above -DI"
    ],
    
    "Downtrend Characteristics": [
        "Price below 20-day and 50-day moving averages",
        "Moving averages sloping downward",
        "Lower highs and lower lows pattern",
        "Strong volume on down moves",
        "ADX above 25 with -DI above +DI"
    ],
    
    "Sideways/Consolidation": [
        "Price oscillating around moving averages",
        "Flat or slightly sloping moving averages",
        "No clear higher highs/lower lows pattern",
        "ADX below 25 indicating weak trend"
    ]
}

ENTRY_EXIT_STRATEGIES = {
    "Long Position Strategy": {
        "Entry Signals": [
            "Bullish candlestick pattern confirmation",
            "Price breaking above resistance",
            "Pullback to support in uptrend",
            "Moving average crossover (bullish)"
        ],
        "Exit Signals": [
            "Take profit at resistance levels",
            "Stop loss below recent support",
            "Bearish reversal pattern",
            "Volume divergence"
        ]
    },
    
    "Short Position Strategy": {
        "Entry Signals": [
            "Bearish candlestick pattern confirmation",
            "Price breaking below support",
            "Rally to resistance in downtrend",
            "Moving average crossover (bearish)"
        ],
        "Exit Signals": [
            "Take profit at support levels",
            "Stop loss above recent resistance",
            "Bullish reversal pattern",
            "Volume divergence"
        ]
    }
}

RISK_MANAGEMENT_RULES = {
    "Position Sizing": [
        "Never risk more than 2% of account per trade",
        "Calculate position size based on stop loss distance",
        "Adjust size based on volatility (ATR)",
        "Consider correlation between positions"
    ],
    
    "Stop Loss Placement": [
        "Below recent swing low for long positions",
        "Above recent swing high for short positions",
        "Use ATR-based stops (1.5-2x ATR)",
        "Avoid placing stops at obvious levels"
    ],
    
    "Take Profit Strategies": [
        "Target previous resistance/support levels",
        "Use risk-reward ratio of at least 1:2",
        "Scale out at multiple targets",
        "Trail stops in trending markets"
    ]
}

def get_pattern_explanation(pattern_name):
    """Get detailed explanation of a candlestick pattern"""
    for category, patterns in CANDLESTICK_PATTERNS.items():
        if pattern_name in patterns:
            return patterns[pattern_name]
    return None

def get_trading_rules():
    """Get comprehensive trading rules and guidelines"""
    return {
        "patterns": CANDLESTICK_PATTERNS,
        "trends": TREND_ANALYSIS_GUIDE,
        "strategies": ENTRY_EXIT_STRATEGIES,
        "risk_management": RISK_MANAGEMENT_RULES
    }