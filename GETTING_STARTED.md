# 🚀 Getting Started with AI Stock Market Analyzer

Welcome to the most comprehensive AI-powered stock market analysis platform! This guide will help you get up and running with all the advanced features.

## 🎯 Quick Start (5 Minutes)

### 1. Install Dependencies
```bash
# Clone the repository
git clone <your-repo-url>
cd ai-stock-market-analyzer

# Run the automated setup
python3 setup.py
```

### 2. Configure API Keys
```bash
# Copy the environment template
cp .env.example .env

# Edit .env with your favorite text editor and add your API keys
nano .env  # or vim .env, or code .env
```

### 3. Launch the Application
```bash
streamlit run app.py
```

🎉 **You're ready to go!** Open your browser to `http://localhost:8501`

---

## 🔧 Detailed Setup Guide

### API Keys Setup

#### 📰 NewsAPI (Free - 1000 requests/month)
1. Visit [NewsAPI.org](https://newsapi.org/register)
2. Create a free account
3. Copy your API key
4. Add to `.env`: `NEWSAPI_KEY=your_key_here`

#### 📈 Finnhub (Free - 60 calls/minute)
1. Visit [Finnhub.io](https://finnhub.io/register)
2. Sign up for free
3. Get your API key from the dashboard
4. Add to `.env`: `FINNHUB_KEY=your_key_here`

#### 🐦 Twitter API v2 (Free - Essential tier)
1. Visit [Twitter Developer Portal](https://developer.twitter.com/)
2. Apply for developer access (usually approved within 24 hours)
3. Create a new app and generate Bearer Token
4. Add to `.env`: `TWITTER_BEARER_TOKEN=your_token_here`

#### 📧 Email Alerts (Optional)
For email notifications, add to `.env`:
```
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
FROM_EMAIL=your_email@gmail.com
```

---

## 🎛️ Feature Overview

### 🏠 **Dashboard Tab**
**What it does:** Main stock analysis with AI predictions
- Enter any stock symbol (AAPL, TSLA, GOOGL, etc.)
- Get technical analysis with 15+ indicators
- AI-powered BUY/SELL/HOLD recommendations
- Confidence scoring and price predictions

**How to use:**
1. Enter stock symbol in sidebar
2. Select date range and interval
3. Click "Analyze & Predict"
4. Review charts, indicators, and AI recommendation

### 📊 **Backtest Tab**
**What it does:** Historical performance analysis
- Compare predictions vs actual performance
- Cumulative returns visualization
- Model accuracy metrics

### 📰 **News/Sentiment Tab**
**What it does:** Real-time market sentiment analysis
- Multi-source news aggregation
- Social media sentiment from Twitter
- Advanced sentiment scoring (TextBlob + VADER)
- Sentiment distribution charts

**How to use:**
1. Enter company name or stock symbol
2. Choose analysis type:
   - **Comprehensive**: All sources combined
   - **News Only**: NewsAPI + Finnhub
   - **Twitter Only**: Social media sentiment
3. Click "🚀 Analyze Sentiment"
4. Review overall sentiment, articles, and tweets

### 🌡️ **Indicators Heatmap Tab**
**What it does:** Technical indicator correlation analysis
- Visualize relationships between indicators
- Identify redundant or complementary signals

### 💼 **Portfolio Simulation Tab**
**What it does:** Multi-stock portfolio optimization
- Sector-based diversification
- AI confidence-weighted allocation
- Risk assessment

### 🚨 **Alerts Tab**
**What it does:** Automated sentiment monitoring
- Set custom sentiment thresholds
- Email notifications when sentiment changes
- Webhook integration for advanced users

**How to use:**
1. Add new alert with symbol and email
2. Set positive/negative sentiment thresholds
3. Configure check interval (5-60 minutes)
4. Receive alerts when sentiment crosses thresholds

### 📊 **Reports Tab**
**What it does:** Data export and professional reporting
- Export sentiment data in multiple formats
- Generate professional HTML reports
- Bulk analysis for multiple symbols
- Historical data storage and retrieval

**How to use:**
1. **Single Export**: Choose symbol, days, and format
2. **Bulk Export**: Enter multiple symbols (one per line)
3. **Auto-Store**: Enable to save all analysis results
4. **Database Stats**: View your analysis history

---

## 📋 Common Use Cases

### 👨‍💼 **For Individual Investors**
1. **Daily Stock Analysis**
   - Use Dashboard tab for technical analysis
   - Check News/Sentiment for market mood
   - Set up alerts for key holdings

2. **Investment Research**
   - Analyze multiple stocks with bulk export
   - Generate HTML reports for documentation
   - Track sentiment trends over time

### 🏢 **For Financial Advisors**
1. **Client Reports**
   - Generate professional HTML reports
   - Export data for presentations
   - Monitor client portfolios with alerts

2. **Market Analysis**
   - Bulk analyze sector stocks
   - Track sentiment across industries
   - Identify market opportunities

### 🎓 **For Students/Researchers**
1. **Academic Research**
   - Export historical sentiment data
   - Analyze correlation between sentiment and price
   - Study market behavior patterns

2. **Learning Finance**
   - Understand technical indicators
   - See how sentiment affects markets
   - Practice investment analysis

---

## 🔧 Troubleshooting

### Common Issues

#### "Module not found" errors
```bash
# Make sure you're in the project directory
cd ai-stock-market-analyzer

# Install requirements
pip install -r requirements.txt

# If using conda
conda install pip
pip install -r requirements.txt
```

#### API key errors
```bash
# Check your .env file
cat .env

# Make sure there are no spaces around the = sign
# Correct: NEWSAPI_KEY=abc123
# Wrong: NEWSAPI_KEY = abc123
```

#### No sentiment data
- Check API status indicators in News/Sentiment tab
- Verify your API keys are active
- Try different search terms
- Check internet connection

#### Email alerts not working
- Use app-specific passwords for Gmail
- Check SMTP settings in .env
- Test with a simple email client first

### Getting Help

1. **Check the logs**: Look for error messages in the terminal
2. **Test components**: Use `python3 demo_sentiment_analysis.py`
3. **Verify setup**: Run `python3 setup.py` again
4. **Check API status**: Visit the API provider websites

---

## 🎨 Advanced Features

### 🤖 **Custom Sentiment Thresholds**
Adjust sensitivity by modifying thresholds in `news_sentiment.py`:
```python
# Default thresholds
POSITIVE_THRESHOLD = 0.1
NEGATIVE_THRESHOLD = -0.1

# More sensitive (catches smaller changes)
POSITIVE_THRESHOLD = 0.05
NEGATIVE_THRESHOLD = -0.05
```

### 📈 **Additional Indicators**
Add custom technical indicators in `app.py`:
```python
def add_custom_indicators(df):
    # Add your custom indicators here
    df['Custom_Signal'] = your_calculation(df)
    return df
```

### 🎯 **Portfolio Customization**
Modify sector definitions in `app.py`:
```python
SECTOR_TICKERS = {
    'Your_Sector': ['STOCK1', 'STOCK2', 'STOCK3'],
    # Add your custom sectors
}
```

### 🔄 **Automated Analysis**
Set up cron jobs for automated analysis:
```bash
# Edit crontab
crontab -e

# Add this line to run analysis every hour
0 * * * * cd /path/to/project && python3 data_export.py --bulk AAPL TSLA GOOGL
```

---

## 📈 Performance Tips

### 🚀 **Speed Optimization**
1. **Use shorter date ranges** for faster analysis
2. **Reduce tweet count** in Twitter analysis
3. **Limit bulk operations** to 5-10 symbols at once
4. **Enable auto-store** to avoid re-analyzing the same data

### 💾 **Data Management**
1. **Regular exports** to avoid losing analysis history
2. **Database cleanup** periodically remove old records
3. **Backup .env file** securely store your API keys

### 🔒 **Security Best Practices**
1. **Never commit .env** to version control
2. **Use app passwords** for email accounts
3. **Rotate API keys** periodically
4. **Monitor API usage** to avoid quota limits

---

## 🎯 Next Steps

### 🌟 **Beginner Path**
1. Start with basic stock analysis on Dashboard
2. Try sentiment analysis for a few stocks
3. Set up one or two alerts
4. Export your first report

### 🚀 **Advanced Path**
1. Set up all API integrations
2. Create comprehensive alerts system
3. Develop custom analysis workflows
4. Build automated reporting pipelines

### 🏆 **Expert Path**
1. Modify algorithms for your specific needs
2. Add new data sources
3. Create custom indicators
4. Build API integrations with other systems

---

## 🎉 Congratulations!

You now have access to a professional-grade stock market analysis platform with:
- ✅ AI-powered predictions
- ✅ Multi-source sentiment analysis
- ✅ Automated alerts
- ✅ Professional reporting
- ✅ Historical data tracking

**Happy Trading!** 📈💰

---

## 📞 Support

- 📧 Check the troubleshooting section above
- 📚 Review the comprehensive README.md
- 🐛 Report issues with detailed error messages
- 💡 Suggest new features or improvements

**Remember:** This tool is for educational purposes only. Always do your own research and consult with financial professionals before making investment decisions.

---

**⚠️ Disclaimer:** Trading and investing involves substantial risk. Past performance does not guarantee future results. This software is provided for educational purposes only and should not be used as the sole basis for investment decisions.