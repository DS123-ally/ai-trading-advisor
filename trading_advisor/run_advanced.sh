#!/bin/bash

echo "🎯 Starting Advanced Trading System..."

# Install TA-Lib dependencies
echo "Installing TA-Lib dependencies..."
pip install --upgrade pip
pip install -r requirements_advanced.txt

# Alternative TA-Lib installation if needed
if ! python3 -c "import talib" 2>/dev/null; then
    echo "Installing TA-Lib binary..."
    pip install --upgrade talib-binary
fi

# Start the advanced trading system
echo "🚀 Launching Advanced Trading System..."
streamlit run advanced_trading_system.py --server.port 8503 --server.address 0.0.0.0

echo "✅ Advanced Trading System started at http://localhost:8503"