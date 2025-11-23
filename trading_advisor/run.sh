#!/bin/bash

echo "🚀 Starting Trading Advisor Application..."

# Install dependencies if not already installed
if [ ! -d "venv" ]; then
    echo "📦 Setting up virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Run the application
echo "🌐 Starting Streamlit app..."
streamlit run complete_trading_app.py --server.port 8501 --server.address 0.0.0.0

echo "✅ Application started!"
echo "🌐 Access at: http://localhost:8501"
echo "🔗 API URL: https://1j1767p10b.execute-api.us-west-2.amazonaws.com/Prod/"