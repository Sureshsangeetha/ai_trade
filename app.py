import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from ta.trend import SMAIndicator, EMAIndicator, MACD, ADXIndicator
from ta.volatility import BollingerBands
from ta.momentum import RSIIndicator, StochasticOscillator
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import datetime
import base64
import os
import streamlit.components.v1 as components

# --- Helper Functions ---
def fetch_data(symbol, start, end, interval="1d"):
    data = yf.download(symbol, start=start, end=end, interval=interval)
    # If no data, return empty DataFrame with OHLCV columns
    if data.empty:
        return pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume'])
    # Flatten columns if MultiIndex (e.g., from yfinance)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = ['_'.join([str(i) for i in col if i]) for col in data.columns.values]
        close_col = f'Close_{symbol}' if f'Close_{symbol}' in data.columns else 'Close'
        data = data.rename(columns={close_col: 'Close'})
        for col in ['Open', 'High', 'Low', 'Volume', 'SMA20', 'SMA50', 'RSI', 'MACD', 'MACD_signal']:
            if f'{col}_{symbol}' in data.columns:
                data = data.rename(columns={f'{col}_{symbol}': col})
    else:
        # Rename columns if needed
        for col in ['Open', 'High', 'Low', 'Volume']:
            if f'{col}_{symbol}' in data.columns:
                data = data.rename(columns={f'{col}_{symbol}': col})
    if 'Close' not in data.columns and (f'Close_{symbol}' in data.columns):
        data = data.rename(columns={f'Close_{symbol}': 'Close'})
    return data

def add_indicators(df):
    close = df['Close']
    if isinstance(close, pd.DataFrame):
        close = close.squeeze()
    df['SMA20'] = SMAIndicator(close, window=20).sma_indicator()
    df['SMA50'] = SMAIndicator(close, window=50).sma_indicator()
    df['EMA20'] = EMAIndicator(close, window=20).ema_indicator()
    df['EMA50'] = EMAIndicator(close, window=50).ema_indicator()
    df['RSI'] = RSIIndicator(close, window=14).rsi()
    macd = MACD(close)
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    bb = BollingerBands(close, window=20, window_dev=2)
    df['BB_High'] = bb.bollinger_hband()
    df['BB_Low'] = bb.bollinger_lband()
    # Only calculate if High/Low exist
    if 'High' in df.columns and 'Low' in df.columns:
        df['Stoch_K'] = StochasticOscillator(df['High'], df['Low'], close, window=14).stoch()
        df['Stoch_D'] = StochasticOscillator(df['High'], df['Low'], close, window=14).stoch_signal()
        df['ADX'] = ADXIndicator(df['High'], df['Low'], close, window=14).adx()
    else:
        df['Stoch_K'] = np.nan
        df['Stoch_D'] = np.nan
        df['ADX'] = np.nan
    df['Pct_Change'] = close.pct_change()
    df['Daily_Return'] = close.pct_change()
    df['Log_Return'] = np.log(close / close.shift(1))
    df['Volatility_20'] = close.pct_change().rolling(window=20).std()
    return df

def get_table_download_link(df):
    csv = df.to_csv(index=True)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings
    href = f'<a href="data:file/csv;base64,{b64}" download="stock_data.csv">Download CSV File</a>'
    return href

# Helper to ensure all OHLCV columns exist
OHLCV_COLS = ['Open', 'High', 'Low', 'Close', 'Volume']
def ensure_ohlcv(df):
    for col in OHLCV_COLS:
        if col not in df.columns:
            df[col] = np.nan
    return df

# --- AI Investment Predictor ---
def prepare_ml_data(df):
    df = df.dropna().copy()
    df['Return'] = df['Close'].pct_change().shift(-1)
    df['Target'] = (df['Return'] > 0).astype(int)
    features = [
        'Open', 'High', 'Low', 'Close', 'Volume',
        'SMA20', 'SMA50', 'EMA20', 'EMA50',
        'RSI', 'MACD', 'MACD_signal',
        'BB_High', 'BB_Low',
        'Stoch_K', 'Stoch_D', 'ADX',
        'Pct_Change', 'Daily_Return', 'Log_Return', 'Volatility_20'
    ]
    # Only use features that exist in df
    features = [f for f in features if f in df.columns]
    X = df[features]
    y = df['Target']
    return X, y

def train_predictor(X, y):
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model, scaler

def predict_investment(model, scaler, latest_row):
    X_latest = scaler.transform([latest_row])
    proba = model.predict_proba(X_latest)[0][1]
    return proba

# --- Streamlit App ---
st.set_page_config(page_title="AI Stock Market Predictor", layout="wide")
st.title("📈 AI Stock Market Technical Analysis & Investment Advisor")

st.sidebar.header("User Input")
symbol = st.sidebar.text_input("Stock Symbol", value="AAPL")
today = datetime.date.today()
def_start = today - datetime.timedelta(days=365)
start_date = st.sidebar.date_input("Start Date", def_start)
end_date = st.sidebar.date_input("End Date", today)
interval = st.sidebar.selectbox("Interval", ["1d", "1h", "30m", "15m", "5m", "1m"], index=0)
investment = st.sidebar.number_input("Investment Amount ($)", min_value=100, value=1000, step=100)

# --- Domains and Top Companies ---
SECTOR_TICKERS = {
    'Technology': ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META'],
    'Healthcare': ['JNJ', 'PFE', 'MRK', 'ABBV', 'TMO'],
    'Finance': ['JPM', 'BAC', 'WFC', 'C', 'GS'],
    'Consumer Discretionary': ['AMZN', 'TSLA', 'HD', 'MCD', 'NKE'],
    'Energy': ['XOM', 'CVX', 'COP', 'SLB', 'EOG'],
    'Industrials': ['UNP', 'HON', 'UPS', 'CAT', 'BA'],
    'Utilities': ['NEE', 'DUK', 'SO', 'AEP', 'EXC'],
    'Materials': ['LIN', 'SHW', 'APD', 'ECL', 'NEM'],
    'Real Estate': ['PLD', 'AMT', 'CCI', 'EQIX', 'PSA'],
    'Communication Services': ['GOOGL', 'META', 'DIS', 'VZ', 'NFLX']
}

st.sidebar.header("Investment Domain")
domain = st.sidebar.selectbox("Select Domain (Sector)", list(SECTOR_TICKERS.keys()))
top_tickers = SECTOR_TICKERS[domain]
total_investment = st.sidebar.number_input("Total Investment Amount ($)", min_value=100, value=5000, step=100)

# --- Streamlit Tabs for Bonus Features ---
tabs = st.tabs(["Dashboard", "Backtest", "News/Sentiment", "Indicators Heatmap", "Portfolio Simulation", "Alerts", "Reports"])

# Import news and sentiment module with error handling
try:
    from news_sentiment import get_news_with_sentiment, analyzer
    SENTIMENT_AVAILABLE = True
except ImportError as e:
    st.warning(f"Sentiment analysis features unavailable: {e}")
    SENTIMENT_AVAILABLE = False
    
try:
    from sentiment_alerts import SentimentAlertManager
    ALERTS_AVAILABLE = True
except ImportError:
    ALERTS_AVAILABLE = False
    
try:
    from data_export import DataExporter
    EXPORT_AVAILABLE = True
except ImportError:
    EXPORT_AVAILABLE = False

with tabs[0]:
    if st.sidebar.button("Analyze & Predict"):
        with st.spinner('Fetching data and running analysis...'):
            df = fetch_data(symbol, start_date, end_date, interval)
            if df.empty:
                st.error("No data found for the selected symbol and date range.")
            else:
                df = add_indicators(df)
                df = ensure_ohlcv(df)
                st.subheader(f"Price & Indicators for {symbol}")
                # Show OHLCV table
                st.markdown("### Price Data (OHLCV)")
                st.dataframe(df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna().tail(30))
                # Enhanced charts using Plotly for better Streamlit Cloud compatibility
                try:
                    import plotly.graph_objects as go
                    from plotly.subplots import make_subplots
                    
                    # Create candlestick chart
                    fig = make_subplots(
                        rows=2, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.03,
                        subplot_titles=('Price & Moving Averages', 'Volume'),
                        row_heights=[0.7, 0.3]
                    )
                    
                    # Candlestick
                    fig.add_trace(
                        go.Candlestick(
                            x=df.index,
                            open=df['Open'],
                            high=df['High'],
                            low=df['Low'],
                            close=df['Close'],
                            name="Price"
                        ),
                        row=1, col=1
                    )
                    
                    # Moving averages
                    fig.add_trace(
                        go.Scatter(x=df.index, y=df['SMA20'], name='SMA20', line=dict(color='blue')),
                        row=1, col=1
                    )
                    fig.add_trace(
                        go.Scatter(x=df.index, y=df['SMA50'], name='SMA50', line=dict(color='red')),
                        row=1, col=1
                    )
                    
                    # Volume
                    fig.add_trace(
                        go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color='lightblue'),
                        row=2, col=1
                    )
                    
                    fig.update_layout(
                        title=f"{symbol} - Price Analysis",
                        xaxis_rangeslider_visible=False,
                        height=600
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                except ImportError:
                    # Fallback to simple line charts
                    st.line_chart(df[['Close', 'SMA20', 'SMA50', 'EMA20', 'EMA50']].dropna())
                st.line_chart(df[['RSI', 'MACD', 'MACD_signal', 'ADX']].dropna())
                st.line_chart(df[['BB_High', 'BB_Low']].dropna())
                st.line_chart(df[['Stoch_K', 'Stoch_D']].dropna())
                # Data Table with all features
                st.markdown("### Data Table (All Features)")
                st.dataframe(df[['Open','High','Low','Close','Volume','SMA20','SMA50','EMA20','EMA50','RSI','MACD','MACD_signal','BB_High','BB_Low','Stoch_K','Stoch_D','ADX']].dropna().tail(30))
                st.markdown(get_table_download_link(df), unsafe_allow_html=True)

                # --- AI Prediction ---
                X, y = prepare_ml_data(df)
                if len(X) > 50:
                    model, scaler = train_predictor(X, y)
                    # Use the same features as in prepare_ml_data
                    features = X.columns
                    latest_row = df.iloc[-1][features].fillna(0).values
                    proba = predict_investment(model, scaler, latest_row)
                    st.subheader("AI Investment Suggestion")
                    if proba > 0.6:
                        st.success(f"Prediction: BUY | Confidence: {proba:.2%}")
                        st.info(f"Suggested Investment: ${investment}")
                        pred_label = 'Buy'
                    elif proba < 0.4:
                        st.warning(f"Prediction: SELL/AVOID | Confidence: {1-proba:.2%}")
                        pred_label = 'Sell/Avoid'
                    else:
                        st.info(f"Prediction: HOLD | Confidence: {proba:.2%}")
                        pred_label = 'Hold'
                    # Next-period price prediction (simple: use last close * (1 + proba * mean return))
                    mean_return = X['Pct_Change'].mean() if 'Pct_Change' in X.columns else 0
                    next_price = df['Close'].iloc[-1] * (1 + proba * mean_return)
                    st.metric("Next-period Price Prediction", f"${next_price:.2f}")
                    # Visualize prediction vs actual
                    st.markdown("### Prediction vs Actual (Backtest)")
                    y_pred = model.predict(scaler.transform(X))
                    pred_series = pd.Series(y_pred, index=df.index[-len(y_pred):])
                    actual_series = y[-len(y_pred):]
                    chart_df = pd.DataFrame({
                        'Close': df['Close'].iloc[-len(y_pred):],
                        'Prediction': pred_series.map({1:'Buy',0:'Sell'}),
                        'Actual': actual_series.map({1:'Buy',0:'Sell'})
                    })
                    st.dataframe(chart_df.tail(30))
                else:
                    st.warning("Not enough data for AI prediction. Try a longer date range.")

        st.write("\n---\n")
        st.caption("This dashboard is for educational purposes only. Not financial advice.")
    else:
        st.info("Enter parameters and click 'Analyze & Predict' to begin.")

    # --- Optional: Custom CSS ---
    st.markdown(
        """
        <style>
        .stButton>button {background-color: #4CAF50; color: white;}
        .stSidebar {background-color: #f0f2f6;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Inject your CSS
    try:
        with open("style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception:
        pass

    # Inject your HTML/JS as a tab (for demo, not for backend logic)
    with st.expander("Show Custom HTML Dashboard (Static Demo)"):
        try:
            with open("index.html") as f:
                components.html(f.read(), height=900, scrolling=True)
        except Exception:
            st.info("index.html not found or cannot be loaded.")

with tabs[1]:
    st.header("Backtesting Results")
    # Show prediction vs actual, cumulative returns, etc.
    # (Reuse chart_df from main prediction section if available)
    try:
        st.dataframe(chart_df.tail(100))
        st.line_chart(chart_df['Close'])
    except Exception:
        st.info("Run an analysis to see backtest results here.")

with tabs[2]:
    st.header("📰 News & Sentiment Analysis")
    
    if not SENTIMENT_AVAILABLE:
        st.error("❌ Sentiment analysis features are not available. This may be due to missing dependencies.")
        st.info("""
        To enable sentiment analysis:
        1. Install required packages: `pip install textblob vaderSentiment tweepy`
        2. Set up API keys in environment variables
        3. Restart the application
        """)
    else:
        # Sidebar controls for news analysis
        st.subheader("Analysis Settings")
        col1, col2 = st.columns(2)
    
    with col1:
        news_query = st.text_input("Search Query (company name or symbol)", value=symbol)
        include_twitter = st.checkbox("Include Twitter Sentiment", value=True)
        
    with col2:
        analysis_type = st.selectbox("Analysis Type", ["Comprehensive", "News Only", "Twitter Only"])
        days_back = st.slider("Days to look back", 1, 7, 3)
    
    if st.button("🚀 Analyze Sentiment", type="primary"):
        with st.spinner("Fetching news and analyzing sentiment across multiple sources..."):
            try:
                # Get comprehensive analysis
                if analysis_type == "Comprehensive":
                    results = analyzer.get_comprehensive_sentiment_analysis(
                        query=news_query, 
                        include_twitter=include_twitter
                    )
                    
                    # Display overall sentiment summary
                    if results['overall_sentiment']:
                        st.success("✅ Analysis Complete!")
                        
                        # Auto-store sentiment data if enabled
                        if st.session_state.get('auto_store', False) and EXPORT_AVAILABLE:
                            try:
                                exporter = DataExporter()
                                exporter.store_sentiment_data(news_query, results)
                                st.success("💾 Sentiment data stored for future reporting")
                            except Exception as e:
                                st.warning(f"Could not store sentiment data: {e}")
                        
                        # Metrics row
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Overall Sentiment", 
                                     results['overall_sentiment']['label'],
                                     f"{results['overall_sentiment']['average_score']:.3f}")
                        with col2:
                            st.metric("Confidence", 
                                     f"{results['overall_sentiment']['confidence']:.1%}")
                        with col3:
                            st.metric("News Articles", 
                                     results['sentiment_summary']['total_articles'])
                        with col4:
                            st.metric("Tweets Analyzed", 
                                     results['sentiment_summary']['total_tweets'])
                        
                        # Sentiment distribution chart
                        st.subheader("Sentiment Distribution")
                        sentiment_data = {
                            'Positive': results['sentiment_summary']['positive_percentage'],
                            'Neutral': results['sentiment_summary']['neutral_percentage'], 
                            'Negative': results['sentiment_summary']['negative_percentage']
                        }
                        st.bar_chart(sentiment_data)
                        
                        # News articles section
                        if results['news_articles']:
                            st.subheader("📑 News Articles")
                            for i, article in enumerate(results['news_articles'][:10]):  # Show top 10
                                with st.expander(f"{article['title'][:80]}..." if len(article['title']) > 80 else article['title']):
                                    col1, col2 = st.columns([3, 1])
                                    with col1:
                                        st.write(article['description'])
                                        st.caption(f"Source: {article['source']} | Published: {article['published_at']}")
                                        if article['url']:
                                            st.markdown(f"[Read Full Article]({article['url']})")
                                    with col2:
                                        sentiment_color = "🟢" if article['sentiment']['compound'] > 0.1 else "🔴" if article['sentiment']['compound'] < -0.1 else "🟡"
                                        st.metric("Sentiment", 
                                                f"{sentiment_color} {article['sentiment']['label']}", 
                                                f"{article['sentiment']['compound']:.3f}")
                        
                        # Twitter sentiment section
                        if results['twitter_sentiment'] and include_twitter:
                            st.subheader("🐦 Twitter Sentiment")
                            
                            # Twitter summary metrics
                            tweet_scores = [tweet['sentiment_compound'] for tweet in results['twitter_sentiment']]
                            avg_twitter_sentiment = sum(tweet_scores) / len(tweet_scores) if tweet_scores else 0
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Average Twitter Sentiment", 
                                         f"{avg_twitter_sentiment:.3f}",
                                         "Positive" if avg_twitter_sentiment > 0 else "Negative" if avg_twitter_sentiment < 0 else "Neutral")
                            with col2:
                                st.metric("Total Tweets", len(results['twitter_sentiment']))
                            
                            # Show sample tweets
                            st.markdown("**Recent Tweets:**")
                            for tweet in results['twitter_sentiment'][:5]:  # Show top 5 tweets
                                sentiment_emoji = "😊" if tweet['sentiment_compound'] > 0.1 else "😞" if tweet['sentiment_compound'] < -0.1 else "😐"
                                st.write(f"{sentiment_emoji} {tweet['text'][:150]}..." if len(tweet['text']) > 150 else f"{sentiment_emoji} {tweet['text']}")
                                st.caption(f"Sentiment: {tweet['sentiment_label']} ({tweet['sentiment_compound']:.2f}) | ❤️ {tweet['like_count']} | 🔄 {tweet['retweet_count']}")
                                st.divider()
                    
                    else:
                        st.warning("No sentiment data found. Please check your API keys and try again.")
                
                elif analysis_type == "News Only":
                    # Legacy news analysis
                    news_results = get_news_with_sentiment(source="newsapi", query=news_query)
                    if news_results:
                        for article in news_results:
                            st.markdown(f"**[{article['title']}]({article['url']})**")
                            st.write(f"Source: {article['source']}")
                            sentiment_color = "🟢" if article['sentiment'] > 0.1 else "🔴" if article['sentiment'] < -0.1 else "🟡"
                            st.write(f"Sentiment: {sentiment_color} {article['sentiment']:.2f}")
                            st.write("---")
                    else:
                        st.info("No news articles found for this query.")
                
                elif analysis_type == "Twitter Only":
                    # Twitter only analysis
                    twitter_data = analyzer.fetch_twitter_sentiment(news_query)
                    if twitter_data:
                        st.success(f"Found {len(twitter_data)} tweets")
                        avg_sentiment = sum(tweet['sentiment_compound'] for tweet in twitter_data) / len(twitter_data)
                        st.metric("Average Sentiment", f"{avg_sentiment:.3f}")
                        
                        for tweet in twitter_data[:10]:
                            sentiment_emoji = "😊" if tweet['sentiment_compound'] > 0.1 else "😞" if tweet['sentiment_compound'] < -0.1 else "😐"
                            st.write(f"{sentiment_emoji} {tweet['text']}")
                            st.caption(f"Sentiment: {tweet['sentiment_label']} | ❤️ {tweet['like_count']} | 🔄 {tweet['retweet_count']}")
                            st.divider()
                    else:
                        st.info("No tweets found or Twitter API not configured.")
                        
            except Exception as e:
                st.error(f"Error during sentiment analysis: {e}")
                st.info("💡 **Tip:** Make sure you have set up your API keys in the `.env` file. See `.env.example` for the required format.")
    
    else:
        # Information about the feature
        st.info("""
        ### 🔄 **Enhanced News & Sentiment Analysis**
        
        This module integrates multiple data sources for comprehensive market sentiment analysis:
        
        **📰 News Sources:**
        - **NewsAPI**: Real-time headlines from major news outlets
        - **Finnhub**: Financial news and company-specific updates
        
        **🐦 Social Media:**
        - **Twitter API v2**: Real-time social sentiment analysis
        
        **🧠 Sentiment Analysis:**
        - **TextBlob**: Polarity and subjectivity analysis
        - **VADER**: Social media optimized sentiment scoring
        - **Composite Scoring**: Combined analysis for improved accuracy
        
        **⚙️ Setup Instructions:**
        1. Copy `.env.example` to `.env`
        2. Add your API keys from NewsAPI, Finnhub, and Twitter
        3. Install requirements: `pip install -r requirements.txt`
        4. Click "Analyze Sentiment" to get started!
        """)
        
        # API Status indicators
        st.subheader("API Status")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if analyzer.NEWSAPI_KEY != "your_newsapi_key_here":
                st.success("✅ NewsAPI Configured")
            else:
                st.warning("⚠️ NewsAPI Not Configured")
        
        with col2:
            if analyzer.FINNHUB_KEY != "your_finnhub_key_here":
                st.success("✅ Finnhub Configured")
            else:
                st.warning("⚠️ Finnhub Not Configured")
        
        with col3:
            if analyzer.twitter_client:
                st.success("✅ Twitter API Configured")
            else:
                st.warning("⚠️ Twitter API Not Configured")

with tabs[3]:
    st.header("Technical Indicators Heatmap")
    try:
        import seaborn as sns
        import matplotlib.pyplot as plt
        indicators = ['SMA20','SMA50','EMA20','EMA50','RSI','MACD','MACD_signal','BB_High','BB_Low','Stoch_K','Stoch_D','ADX']
        corr = df[indicators].corr()
        fig, ax = plt.subplots()
        sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
        st.pyplot(fig)
    except Exception:
        st.info("Run an analysis to see the indicators heatmap.")

with tabs[4]:
    st.header("Portfolio Simulation")
    st.info("Portfolio simulation coming soon! (Simulate returns based on AI allocation and show a chart)")

with tabs[5]:
    st.header("🚨 Sentiment Alerts")
    
    if not ALERTS_AVAILABLE:
        st.error("❌ Alert features are not available due to missing dependencies.")
        st.info("Install required packages and restart the application to enable alerts.")
    else:
        # Initialize alert manager
        try:
            alert_manager = SentimentAlertManager()
        
        # Alert management interface
        st.subheader("Alert Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Add New Alert")
            new_symbol = st.text_input("Stock Symbol", value="AAPL", key="alert_symbol")
            new_email = st.text_input("Email Address", key="alert_email")
            
            col1a, col1b = st.columns(2)
            with col1a:
                pos_threshold = st.number_input("Positive Threshold", min_value=-1.0, max_value=1.0, value=0.5, step=0.1)
            with col1b:
                neg_threshold = st.number_input("Negative Threshold", min_value=-1.0, max_value=1.0, value=-0.5, step=0.1)
            
            check_interval = st.selectbox("Check Interval", [5, 10, 15, 30, 60], index=2) * 60  # Convert to seconds
            
            if st.button("Add Alert", type="primary"):
                if new_symbol and new_email:
                    alert_manager.add_alert(
                        symbol=new_symbol,
                        threshold_positive=pos_threshold,
                        threshold_negative=neg_threshold,
                        email=new_email,
                        check_interval=check_interval
                    )
                    st.success(f"✅ Alert added for {new_symbol}")
                    st.rerun()
                else:
                    st.error("Please provide both symbol and email address")
        
        with col2:
            st.markdown("#### Current Alerts")
            if alert_manager.alerts:
                for i, alert in enumerate(alert_manager.alerts):
                    with st.expander(f"{alert.symbol} - {alert.email}"):
                        st.write(f"**Thresholds:** +{alert.threshold_positive}, {alert.threshold_negative}")
                        st.write(f"**Check Interval:** {alert.check_interval // 60} minutes")
                        
                        if alert.last_checked:
                            st.write(f"**Last Checked:** {alert.last_checked.strftime('%Y-%m-%d %H:%M:%S')}")
                        if alert.last_sentiment is not None:
                            st.write(f"**Last Sentiment:** {alert.last_sentiment:.3f}")
                        
                        st.write(f"**Alerts Triggered:** {len(alert.alert_history)}")
                        
                        if st.button(f"Remove {alert.symbol}", key=f"remove_{i}"):
                            alert_manager.remove_alert(alert.symbol)
                            st.success(f"Removed alert for {alert.symbol}")
                            st.rerun()
            else:
                st.info("No alerts configured yet")
        
        # Alert summary
        st.subheader("Alert Summary")
        summary = alert_manager.get_alert_summary()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Alerts", summary['total_alerts'])
        with col2:
            st.metric("Active Alerts", summary['active_alerts'])
        with col3:
            st.metric("Alerts Today", summary['alerts_triggered_today'])
        
        # Manual alert check
        st.subheader("Manual Alert Check")
        if st.button("🔍 Check All Alerts Now"):
            with st.spinner("Checking all alerts..."):
                alert_manager.check_all_alerts()
                st.success("✅ Alert check completed")
        
        # Recent alert history
        if summary['alerts']:
            st.subheader("Recent Alert Activity")
            for alert_info in summary['alerts']:
                if alert_info['alerts_today'] > 0:
                    st.write(f"🔔 {alert_info['symbol']}: {alert_info['alerts_today']} alerts today")
        
        except Exception as e:
            st.error(f"Error loading alerts: {e}")
            st.info("Make sure all required dependencies are installed")

with tabs[6]:
    st.header("📊 Data Export & Reports")
    
    if not EXPORT_AVAILABLE:
        st.error("❌ Export and reporting features are not available due to missing dependencies.")
        st.info("Install required packages and restart the application to enable data export.")
    else:
        # Initialize data exporter
        try:
            exporter = DataExporter()
        
        # Export options
        st.subheader("Export Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Single Symbol Export")
            export_symbol = st.text_input("Symbol to Export", value=symbol, key="export_symbol")
            export_days = st.slider("Days to Include", 1, 90, 30)
            export_format = st.selectbox("Export Format", ["CSV", "JSON", "HTML Report"])
            
            if st.button("📥 Export Data", type="primary"):
                with st.spinner(f"Exporting {export_symbol} data..."):
                    try:
                        if export_format == "CSV":
                            filename = exporter.export_to_csv(export_symbol, export_days)
                        elif export_format == "JSON":
                            filename = exporter.export_to_json(export_symbol, export_days)
                        elif export_format == "HTML Report":
                            filename = exporter.generate_html_report(export_symbol, export_days)
                        
                        if filename:
                            st.success(f"✅ Data exported to {filename}")
                            
                            # Provide download link
                            if os.path.exists(filename):
                                with open(filename, 'rb') as file:
                                    st.download_button(
                                        label=f"Download {filename}",
                                        data=file.read(),
                                        file_name=filename,
                                        mime="text/csv" if export_format == "CSV" else "application/json" if export_format == "JSON" else "text/html"
                                    )
                        else:
                            st.error("❌ Export failed")
                    except Exception as e:
                        st.error(f"Export error: {e}")
        
        with col2:
            st.markdown("#### Bulk Export")
            bulk_symbols = st.text_area("Symbols (one per line)", value="AAPL\nTSLA\nGOOGL\nMSFT", key="bulk_symbols")
            bulk_format = st.selectbox("Bulk Export Format", ["CSV", "JSON", "HTML Report"], key="bulk_format")
            
            if st.button("📦 Bulk Export", type="primary"):
                symbols_list = [s.strip().upper() for s in bulk_symbols.split('\n') if s.strip()]
                
                if symbols_list:
                    with st.spinner(f"Analyzing and exporting {len(symbols_list)} symbols..."):
                        try:
                            results = exporter.bulk_analysis_and_export(symbols_list, bulk_format.lower())
                            
                            successful = sum(1 for r in results.values() if r['status'] == 'success')
                            st.success(f"✅ Successfully exported {successful}/{len(symbols_list)} symbols")
                            
                            # Show results
                            for symbol, result in results.items():
                                if result['status'] == 'success':
                                    st.write(f"✅ {symbol}: {result['sentiment']['label']} ({result['sentiment']['average_score']:.3f})")
                                else:
                                    st.write(f"❌ {symbol}: {result.get('error', 'Unknown error')}")
                        except Exception as e:
                            st.error(f"Bulk export error: {e}")
                else:
                    st.error("Please enter at least one symbol")
        
        # Database statistics
        st.subheader("Database Statistics")
        stats = exporter.get_database_stats()
        
        if stats:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Records", stats.get('total_records', 0))
            with col2:
                st.metric("Unique Symbols", stats.get('unique_symbols', 0))
            with col3:
                date_range = stats.get('date_range', {})
                if date_range.get('earliest'):
                    days_span = (datetime.now() - datetime.fromisoformat(date_range['earliest'])).days
                    st.metric("Data Span (Days)", days_span)
            
            # Top symbols
            if stats.get('top_symbols'):
                st.markdown("#### Most Analyzed Symbols")
                for symbol_data in stats['top_symbols'][:5]:
                    st.write(f"📈 {symbol_data['symbol']}: {symbol_data['count']} records")
        
        # Auto-store sentiment data
        st.subheader("⚙️ Auto-Store Settings")
        st.info("Enable automatic storage of sentiment analysis results for future reporting")
        
        if 'auto_store' not in st.session_state:
            st.session_state.auto_store = False
        
        auto_store = st.checkbox("Automatically store sentiment analysis results", value=st.session_state.auto_store)
        st.session_state.auto_store = auto_store
        
        if auto_store:
            st.success("✅ Auto-store enabled - sentiment data will be saved to database")
        
                     except Exception as e:
            st.error(f"Error loading data export features: {e}")
            st.info("Make sure all required dependencies are installed")

if st.sidebar.button("AI Portfolio Suggestion"):
    st.subheader(f"AI Portfolio Suggestion for {domain}")
    results = []
    for ticker in top_tickers:
        df = fetch_data(ticker, start_date, end_date)
        if df.empty:
            continue
        df = add_indicators(df)
        df = ensure_ohlcv(df)
        # Show OHLCV table for each company
        st.markdown(f"#### Price Data (OHLCV) for {ticker}")
        st.dataframe(df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna().tail(30))
        X, y = prepare_ml_data(df)
        if len(X) > 50:
            model, scaler = train_predictor(X, y)
            features = X.columns
            latest_row = df.iloc[-1][features].fillna(0).values
            proba = predict_investment(model, scaler, latest_row)
            results.append({'Company': ticker, 'Confidence': proba})
    if results:
        # Sort by confidence and allocate more to higher confidence
        results = sorted(results, key=lambda x: x['Confidence'], reverse=True)
        total_conf = sum([r['Confidence'] for r in results if r['Confidence'] > 0.5])
        for r in results:
            if r['Confidence'] > 0.5 and total_conf > 0:
                r['Suggested Investment'] = round(total_investment * r['Confidence'] / total_conf, 2)
            else:
                r['Suggested Investment'] = 0
        df_results = pd.DataFrame(results)
        df_results['Domain'] = domain
        st.dataframe(df_results[['Company', 'Domain', 'Confidence', 'Suggested Investment']])
        st.caption("Companies with confidence > 0.5 are considered for investment. Allocation is proportional to AI confidence.")
    else:
        st.warning("No suitable companies found for this domain and date range.")

# API keys are now managed in .env file through the news_sentiment module
