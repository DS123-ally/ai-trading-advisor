#!/bin/bash

echo "Starting Trading Advisor Backend..."

# Create data directory
mkdir -p data

# Install dependencies
pip install -r requirements.txt

# Start Flask API directly
python3 api/main.py

echo "Backend services started!"
echo "API: http://localhost:5000"
echo "Health check: http://localhost:5000/health"
echo ""
echo "Available endpoints:"
echo "GET /api/stock/<symbol> - Get stock data"
echo "GET /api/signals/<symbol> - Get trading signals"
echo "GET /api/portfolio/<user_id> - Get portfolio"
echo "GET /api/alerts - Get market alerts"
echo "GET /api/analysis/sector - Get sector analysis"
echo "POST /api/screener - Screen stocks"