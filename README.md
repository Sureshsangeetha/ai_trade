# 📈 AI Stock Market Technical Analysis & Investment Advisor

A comprehensive AI-powered stock market analysis platform that combines technical indicators, machine learning predictions, and real-time sentiment analysis to provide intelligent investment insights.

## 🚀 Features

### 🔍 **Technical Analysis**
- Multiple technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands, Stochastic, ADX)
- Interactive candlestick charts with moving averages
- Correlation heatmaps for indicator analysis
- Volatility and momentum analysis

### 🤖 **AI-Powered Predictions**
- Random Forest machine learning model for price prediction
- Confidence-based investment recommendations (BUY/SELL/HOLD)
- Backtesting and performance evaluation
- Portfolio optimization across multiple sectors

### 📰 **Enhanced News & Sentiment Analysis**
- **Multi-source news aggregation**: NewsAPI, Finnhub
- **Social media sentiment**: Twitter API v2 integration
- **Advanced sentiment scoring**: TextBlob + VADER combined analysis
- **Real-time market sentiment**: Comprehensive analysis dashboard
- **Historical sentiment tracking**: Up to 7 days lookback

### 📊 **Portfolio Management**
- Sector-based portfolio suggestions
- AI confidence-weighted allocations
- Risk assessment and diversification
- Performance tracking and simulation

## 🛠️ Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd ai-stock-market-analyzer
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. API Keys Configuration

#### Copy the environment template:
```bash
cp .env.example .env
```

#### Get your API keys and update `.env`:

**📰 NewsAPI** (Free tier: 1000 requests/month)
1. Visit [NewsAPI.org](https://newsapi.org/register)
2. Register for a free account
3. Copy your API key to `.env`:
   ```
   NEWSAPI_KEY=your_actual_newsapi_key_here
   ```

**📈 Finnhub** (Free tier: 60 calls/minute)
1. Visit [Finnhub.io](https://finnhub.io/register)
2. Register for a free account
3. Copy your API key to `.env`:
   ```
   FINNHUB_KEY=your_actual_finnhub_key_here
   ```

**🐦 Twitter API v2** (Essential tier: Free)
1. Visit [Twitter Developer Portal](https://developer.twitter.com/)
2. Apply for developer access
3. Create a new app and get Bearer Token
4. Copy your bearer token to `.env`:
   ```
   TWITTER_BEARER_TOKEN=your_actual_twitter_bearer_token_here
   ```

### 4. Run the Application
```bash
streamlit run app.py
```

## 🌐 **Hosting Your Application**

### **🚀 Quick Deployment (Recommended)**
```bash
python3 deploy.py
```
This interactive script will guide you through deploying to your preferred platform.

### **☁️ Hosting Options**

| Platform | Cost | Difficulty | Best For |
|----------|------|------------|----------|
| **Streamlit Cloud** | Free | ⭐ Easy | Personal, demos |
| **Railway** | $5/month | ⭐⭐ Easy | Small teams |
| **Digital Ocean** | $10/month | ⭐⭐⭐ Medium | Production |
| **AWS/GCP/Azure** | $15+/month | ⭐⭐⭐⭐ Hard | Enterprise |

### **�️ Streamlit Cloud Deployment Issues?**
If you're getting dependency errors on Streamlit Cloud:
```bash
python3 fix_deployment.py
# Follow the prompts to switch to cloud-optimized version
```

### **�📖 Detailed Instructions**
- `STREAMLIT_CLOUD_FIX.md` - Fix deployment errors
- `DEPLOYMENT_GUIDE.md` - Comprehensive hosting guide

## 📱 Usage Guide

### 🎯 **Basic Stock Analysis**
1. Enter a stock symbol (e.g., AAPL, TSLA, MSFT)
2. Select date range and interval
3. Click "Analyze & Predict" for comprehensive analysis

### 📰 **News & Sentiment Analysis**
1. Navigate to the "News/Sentiment" tab
2. Enter a company name or stock symbol
3. Choose analysis type:
   - **Comprehensive**: All sources + Twitter sentiment
   - **News Only**: NewsAPI + Finnhub articles
   - **Twitter Only**: Social media sentiment
4. Click "🚀 Analyze Sentiment"

### 💼 **Portfolio Optimization**
1. Select a market sector from the sidebar
2. Set total investment amount
3. Click "AI Portfolio Suggestion" for optimized allocation

## 🔧 Advanced Configuration

### Environment Variables
```bash
# Required for news and sentiment analysis
NEWSAPI_KEY=your_newsapi_key
FINNHUB_KEY=your_finnhub_key
TWITTER_BEARER_TOKEN=your_twitter_bearer_token

# Optional settings
ENVIRONMENT=development  # or production
```

### Customization Options
- Modify `SECTOR_TICKERS` in `app.py` to add/remove sectors
- Adjust sentiment thresholds in `news_sentiment.py`
- Customize ML model parameters in the `train_predictor` function

## 📊 Sentiment Analysis Details

### **Scoring System**
- **Range**: -1.0 (most negative) to +1.0 (most positive)
- **Thresholds**: 
  - Positive: > 0.1
  - Neutral: -0.1 to 0.1  
  - Negative: < -0.1

### **Analysis Methods**
1. **TextBlob**: General purpose sentiment analysis
2. **VADER**: Social media optimized scoring
3. **Composite Score**: Weighted average of both methods

### **Data Sources**
- **News Articles**: Recent headlines and descriptions
- **Social Media**: Real-time tweets with engagement metrics
- **Financial News**: Company-specific updates from Finnhub

## 🚨 Limitations & Disclaimers

- **Educational Purpose**: This tool is for educational and research purposes only
- **Not Financial Advice**: Do not use for actual investment decisions without consulting professionals
- **API Rate Limits**: Free tier APIs have usage limitations
- **Market Volatility**: Past performance doesn't guarantee future results
- **Sentiment Accuracy**: Sentiment analysis is approximate and should be combined with other factors

## 🔧 Troubleshooting

### Common Issues

**1. API Key Errors**
```
Error: Invalid API key
```
- Verify your API keys in `.env` file
- Check that you have active subscriptions to the APIs
- Ensure no extra spaces or quotes around keys

**2. Twitter API Access**
```
Error: Twitter API setup failed
```
- Verify you have Essential tier access (free)
- Check your Bearer Token is correct
- Ensure your Twitter developer account is approved

**3. No Data Returned**
```
No news articles found
```
- Try different search terms
- Check if APIs are working (status indicators in app)
- Verify internet connection

**4. Installation Issues**
```
ModuleNotFoundError: No module named 'tweepy'
```
- Run: `pip install -r requirements.txt`
- If using conda: `conda install pip` then retry

## 📈 Future Enhancements

- [ ] Real-time price alerts and notifications
- [ ] Additional news sources (Alpha Vantage, Quandl)
- [ ] Options and futures analysis
- [ ] Advanced ML models (LSTM, Transformer)
- [ ] Crypto currency support
- [ ] Risk management tools
- [ ] Mobile app development

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **yfinance**: Yahoo Finance data
- **Streamlit**: Web app framework
- **NewsAPI**: News aggregation service
- **Finnhub**: Financial data provider
- **Twitter API**: Social media sentiment data
- **Technical Analysis Library**: TA indicators

---

**⚠️ Risk Warning**: Trading and investing in financial markets involves substantial risk of loss and is not suitable for every investor. The high degree of leverage can work against you as well as for you. Before deciding to trade or invest, you should carefully consider your investment objectives, level of experience, and risk appetite.