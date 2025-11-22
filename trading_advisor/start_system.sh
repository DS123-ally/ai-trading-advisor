#!/bin/bash

echo "🚀 Trading Advisor System Launcher"
echo "=================================="
echo ""
echo "Choose your system:"
echo "1. 🎯 Quick Start Demo (Beginner-friendly)"
echo "2. 📊 Advanced Trading System (Professional)"
echo "3. 🔗 API Integration System (Multi-source)"
echo "4. 🌐 Gateway API Service (Production)"
echo ""

read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo "🎯 Starting Quick Start Demo..."
        streamlit run quick_start.py --server.port 8501
        ;;
    2)
        echo "📊 Starting Advanced Trading System..."
        ./run_advanced.sh
        ;;
    3)
        echo "🔗 Starting API Integration System..."
        ./run_api_system.sh
        ;;
    4)
        echo "🌐 Starting Gateway API Service..."
        python3 gateway_api.py
        ;;
    *)
        echo "❌ Invalid choice. Please run again."
        ;;
esac