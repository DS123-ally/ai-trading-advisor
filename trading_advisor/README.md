# 🚀 AI Trading Advisor Platform

A comprehensive trading platform with real-time market data, AI-powered analysis, and intelligent chatbot assistance.

## ✨ Features

- 📊 **Real-time Market Data** - Live stock prices and analysis
- 🤖 **AI Trading Assistant** - Intelligent chatbot with market insights
- 📈 **Advanced Analytics** - Technical indicators, candlestick patterns
- 💼 **Portfolio Management** - Track positions and P&L
- 🔍 **Stock Screener** - Custom filtering and analysis
- 🌐 **API Backend** - RESTful services with AWS integration

## 🚀 Quick Start

### Option 1: Simple Demo
```bash
python3 simple_chatbot.py
streamlit run simple_chatbot.py
```

### Option 2: Complete Platform
```bash
streamlit run complete_trading_app.py
```

### Option 3: Advanced Analysis
```bash
streamlit run advanced_trading_system.py
```

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/yourusername/trading-advisor.git
cd trading-advisor

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run complete_trading_app.py
```

## 🔧 Configuration

1. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`
2. Add your API keys:
```toml
ALPHA_VANTAGE_KEY = "your_key_here"
AWS_ACCESS_KEY_ID = "your_aws_key"
```

## 📊 Applications

| App | Description | Features |
|-----|-------------|----------|
| `simple_chatbot.py` | Basic trading assistant | Stock prices, basic advice |
| `complete_trading_app.py` | Full platform | Dashboard, portfolio, AI chat |
| `advanced_trading_system.py` | Professional analysis | Patterns, signals, plans |
| `gateway_api.py` | Backend API | REST endpoints, AWS ready |

## 🤖 AI Chatbot Features

- **Smart Symbol Detection** - Automatically recognizes stock symbols
- **Personalized Advice** - Based on risk tolerance and style
- **Real-time Analysis** - Live market data integration
- **Trading Education** - Strategies, risk management, patterns
- **Portfolio Guidance** - Diversification and allocation tips

## 📈 Technical Analysis

- **Candlestick Patterns** - 20+ pattern recognition
- **Technical Indicators** - RSI, SMA, EMA, MACD
- **Support/Resistance** - Automatic level detection
- **Trading Signals** - BUY/SELL/HOLD recommendations
- **Risk Assessment** - Volatility and risk metrics

## 🌐 API Endpoints

```
GET  /api/stock/{symbol}        # Stock data
GET  /api/analysis/{symbol}     # AI analysis
GET  /api/signals/{symbol}      # Trading signals
GET  /api/portfolio/{user_id}   # Portfolio data
POST /api/screener              # Stock screening
```

## 🚀 Deployment

### AWS Lambda + API Gateway
```bash
./deploy_gateway.sh
```

### Docker
```bash
docker-compose up
```

### Local Development
```bash
python3 gateway_api.py  # Backend API
streamlit run complete_trading_app.py  # Frontend
```

## 📚 Documentation

- **Pattern Library** - `pattern_library.py` - Educational content
- **API Reference** - `api_endpoints.py` - Integration examples
- **User Guide** - `README_FINAL.md` - Complete documentation

## 🛠️ Tech Stack

- **Frontend**: Streamlit, Plotly, Pandas
- **Backend**: Flask, SQLite, Redis
- **AI/ML**: AWS Bedrock (Titan), Technical Analysis
- **Data**: Yahoo Finance, Alpha Vantage, Polygon
- **Deployment**: AWS Lambda, API Gateway, Docker

## 📊 Screenshots

### Dashboard
![Dashboard](https://via.placeholder.com/800x400?text=Trading+Dashboard)

### AI Chatbot
![Chatbot](https://via.placeholder.com/800x400?text=AI+Trading+Assistant)

### Technical Analysis
![Analysis](https://via.placeholder.com/800x400?text=Technical+Analysis)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This software is for educational purposes only. Not financial advice. Trading involves risk of loss.

## 🙏 Acknowledgments

- Yahoo Finance for market data
- AWS Bedrock for AI capabilities
- Streamlit for the amazing framework
- Open source community

---

⭐ **Star this repo if you found it helpful!**