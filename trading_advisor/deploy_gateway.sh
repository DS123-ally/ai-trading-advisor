#!/bin/bash

echo "🌐 Deploying Trading API Gateway..."

# Install dependencies
pip install -r requirements_bedrock.txt -t .

# Deploy using SAM
sam build -t gateway_template.yaml
sam deploy --template-file gateway_template.yaml --guided

echo "✅ API Gateway deployed!"
echo ""
echo "📊 Available endpoints:"
echo "GET  /stock/{symbol} - Get stock data"
echo "GET  /analysis/{symbol} - Get AI analysis"
echo "GET  /signals/{symbol} - Get trading signals"
echo "GET  /portfolio - Get portfolio data"
echo "GET  /market-overview - Get market overview"
echo "POST /screener - Screen stocks"
echo "GET  /health - Health check"