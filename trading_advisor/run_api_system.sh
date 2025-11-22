#!/bin/bash

echo "🔗 Starting API-Integrated Trading System..."

# Install additional API dependencies
pip install requests boto3 alpha-vantage polygon-api-client

# Set environment variables if not using secrets.toml
export STREAMLIT_SERVER_PORT=8504
export STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Start the API-integrated system
streamlit run api_integration.py --server.port 8504 --server.address 0.0.0.0

echo "✅ API Trading System started at http://localhost:8504"