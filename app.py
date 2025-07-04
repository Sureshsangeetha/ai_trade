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
tabs = st.tabs(["Dashboard", "Backtest", "News/Sentiment", "Indicators Heatmap", "Portfolio Simulation"])

# Import news and sentiment module
from news_sentiment import get_news_with_sentiment

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
                # Candlestick chart (if mplfinance is available)
                try:
                    import mplfinance as mpf
                    import matplotlib.pyplot as plt
                    import io
                    fig, ax = plt.subplots(figsize=(8,4))
                    mpf.plot(df.tail(60), type='candle', ax=ax, mav=(20,50), volume=True, style='yahoo')
                    buf = io.BytesIO()
                    plt.savefig(buf, format='png')
                    st.image(buf)
                except ImportError:
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
    st.header("News & Sentiment")
    news_source = st.selectbox("Select News Source", ["newsapi", "finnhub"])
    news_query = st.text_input("News Query (company name or symbol)", value=symbol)
    if st.button("Fetch News & Sentiment"):
        with st.spinner("Fetching news and analyzing sentiment..."):
            try:
                news_results = get_news_with_sentiment(source=news_source, query=news_query)
                if news_results:
                    for article in news_results:
                        st.markdown(f"**[{article['title']}]({article['url']})**")
                        st.write(f"Source: {article['source']}")
                        st.write(f"Sentiment Score: {article['sentiment']:.2f}")
                        st.write("---")
                else:
                    st.info("No news articles found for this query.")
            except Exception as e:
                st.error(f"Error fetching news or sentiment: {e}")
    else:
        st.info("We're currently developing the News and Sentiment Analysis module. Integration with NewsAPI, Finnhub, and Twitter API is in progress to fetch real-time headlines and perform sentiment scoring. This feature will be available soon to enhance prediction accuracy and user insights.")

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

# News API keys (for demonstration, these should be kept secret)
NEWSAPI_KEY='your_newsapi_key'
FINNHUB_KEY='your_finnhub_key'
