import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import json

# Page config
st.set_page_config(page_title="AI Stock Analyzer", layout="wide")

# Title
st.title("📈 AI Stock Market Analyzer")
st.write("**Real-time data powered by Alpha Vantage API**")

# Alpha Vantage API functions
def get_stock_data(symbol, api_key=None):
    """Get real-time stock data from Alpha Vantage"""
    if not api_key:
        # Return sample data if no API key
        return generate_sample_data(symbol)
    
    try:
        # Get daily data
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if "Time Series (Daily)" in data:
            ts = data["Time Series (Daily)"]
            df = pd.DataFrame(ts).T
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            
            # Convert to numeric
            df = df.apply(pd.to_numeric)
            
            # Rename columns
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            
            return df
        else:
            st.warning("⚠️ API limit reached or invalid symbol. Using sample data.")
            return generate_sample_data(symbol)
            
    except Exception as e:
        st.warning(f"⚠️ API error: {str(e)}. Using sample data.")
        return generate_sample_data(symbol)

def generate_sample_data(symbol, days=365):
    """Generate realistic sample stock data"""
    np.random.seed(hash(symbol) % 1000)
    
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    # Base prices for different stocks
    base_prices = {
        'AAPL': 150,
        'TSLA': 200,
        'GOOGL': 2500,
        'MSFT': 300,
        'AMZN': 3000,
        'META': 250,
        'NVDA': 400,
        'NFLX': 350,
        'AMD': 100,
        'INTC': 50
    }
    
    base_price = base_prices.get(symbol, 100)
    
    # Generate realistic price movements
    returns = np.random.normal(0.001, 0.02, days)
    prices = [base_price]
    
    for i in range(1, days):
        new_price = prices[-1] * (1 + returns[i])
        prices.append(max(new_price, 1))
    
    # Create OHLCV data
    data = pd.DataFrame(index=dates)
    data['Close'] = prices
    data['Open'] = data['Close'].shift(1) * (1 + np.random.normal(0, 0.005, days))
    data['High'] = data[['Open', 'Close']].max(axis=1) * (1 + np.abs(np.random.normal(0, 0.01, days)))
    data['Low'] = data[['Open', 'Close']].min(axis=1) * (1 - np.abs(np.random.normal(0, 0.01, days)))
    data['Volume'] = np.random.randint(1000000, 50000000, days)
    
    # Fill NaN values
    data = data.fillna(method='bfill')
    
    return data

# Sidebar
st.sidebar.header("📊 Stock Analysis")

# API Key input
api_key = st.sidebar.text_input("🔑 Alpha Vantage API Key (optional)", 
                               type="password", 
                               help="Get free API key at https://www.alphavantage.co/support/#api-key")

# Stock selection
symbol = st.sidebar.selectbox("Select Stock", 
                             ["AAPL", "TSLA", "GOOGL", "MSFT", "AMZN", 
                              "META", "NVDA", "NFLX", "AMD", "INTC"])

# Analysis button
analyze_btn = st.sidebar.button("🚀 Analyze Stock", type="primary")

if analyze_btn:
    # Get stock data
    with st.spinner(f"Analyzing {symbol}..."):
        data = get_stock_data(symbol, api_key)
    
    # Check if using real or sample data
    if api_key:
        st.success("✅ Using real-time data from Alpha Vantage")
    else:
        st.info("ℹ️ Using sample data. Add API key for real-time data.")
    
    # Latest price info
    latest = data.iloc[-1]
    prev = data.iloc[-2]
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    price_change = latest['Close'] - prev['Close']
    price_change_pct = (price_change / prev['Close']) * 100
    
    with col1:
        st.metric("Current Price", f"${latest['Close']:.2f}", 
                 f"{price_change:+.2f} ({price_change_pct:+.2f}%)")
    with col2:
        st.metric("Volume", f"{int(latest['Volume']):,}")
    with col3:
        st.metric("High", f"${latest['High']:.2f}")
    with col4:
        st.metric("Low", f"${latest['Low']:.2f}")
    
    # Chart
    st.subheader("📈 Price Chart")
    st.line_chart(data['Close'].tail(90))
    
    # Moving averages
    data['SMA_20'] = data['Close'].rolling(window=20).mean()
    data['SMA_50'] = data['Close'].rolling(window=50).mean()
    data['EMA_12'] = data['Close'].ewm(span=12).mean()
    data['EMA_26'] = data['Close'].ewm(span=26).mean()
    
    # Chart with moving averages
    st.subheader("📊 Price with Moving Averages")
    chart_data = pd.DataFrame({
        'Close': data['Close'],
        'SMA 20': data['SMA_20'],
        'SMA 50': data['SMA_50'],
        'EMA 12': data['EMA_12']
    })
    st.line_chart(chart_data.dropna().tail(90))
    
    # Technical indicators
    st.subheader("📈 Technical Analysis")
    
    # RSI calculation
    def calculate_rsi(prices, period=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    data['RSI'] = calculate_rsi(data['Close'])
    
    # MACD
    data['MACD'] = data['EMA_12'] - data['EMA_26']
    data['MACD_Signal'] = data['MACD'].ewm(span=9).mean()
    
    # Bollinger Bands
    data['BB_Middle'] = data['Close'].rolling(window=20).mean()
    data['BB_Upper'] = data['BB_Middle'] + (data['Close'].rolling(window=20).std() * 2)
    data['BB_Lower'] = data['BB_Middle'] - (data['Close'].rolling(window=20).std() * 2)
    
    # Technical indicators display
    col1, col2, col3 = st.columns(3)
    
    with col1:
        rsi_value = data['RSI'].iloc[-1]
        if rsi_value > 70:
            st.metric("RSI (14)", f"{rsi_value:.1f}", "Overbought", delta_color="inverse")
        elif rsi_value < 30:
            st.metric("RSI (14)", f"{rsi_value:.1f}", "Oversold", delta_color="normal")
        else:
            st.metric("RSI (14)", f"{rsi_value:.1f}", "Neutral")
    
    with col2:
        macd_value = data['MACD'].iloc[-1]
        macd_signal = data['MACD_Signal'].iloc[-1]
        macd_diff = macd_value - macd_signal
        st.metric("MACD", f"{macd_value:.2f}", f"{macd_diff:+.2f}")
    
    with col3:
        bb_position = (latest['Close'] - data['BB_Lower'].iloc[-1]) / (data['BB_Upper'].iloc[-1] - data['BB_Lower'].iloc[-1])
        st.metric("BB Position", f"{bb_position:.2f}", f"{bb_position*100:.0f}%")
    
    # AI Analysis
    st.subheader("🤖 AI Analysis")
    
    latest_price = latest['Close']
    sma_20 = data['SMA_20'].iloc[-1]
    sma_50 = data['SMA_50'].iloc[-1]
    
    signals = []
    score = 0
    
    # Price vs MA signals
    if latest_price > sma_20:
        signals.append("✅ Price above 20-day MA (Bullish)")
        score += 1
    else:
        signals.append("❌ Price below 20-day MA (Bearish)")
        score -= 1
    
    if latest_price > sma_50:
        signals.append("✅ Price above 50-day MA (Bullish)")
        score += 1
    else:
        signals.append("❌ Price below 50-day MA (Bearish)")
        score -= 1
    
    if sma_20 > sma_50:
        signals.append("✅ Short-term trend positive")
        score += 1
    else:
        signals.append("❌ Short-term trend negative")
        score -= 1
    
    # RSI signals
    if rsi_value > 70:
        signals.append("⚠️ RSI Overbought (Sell signal)")
        score -= 1
    elif rsi_value < 30:
        signals.append("✅ RSI Oversold (Buy signal)")
        score += 1
    else:
        signals.append("➡️ RSI Neutral")
    
    # MACD signals
    if macd_value > macd_signal:
        signals.append("✅ MACD Bullish crossover")
        score += 1
    else:
        signals.append("❌ MACD Bearish crossover")
        score -= 1
    
    # Volume analysis
    avg_volume = data['Volume'].rolling(window=20).mean().iloc[-1]
    if latest['Volume'] > avg_volume * 1.5:
        signals.append("✅ High volume (Strong signal)")
        score += 0.5
    elif latest['Volume'] < avg_volume * 0.5:
        signals.append("⚠️ Low volume (Weak signal)")
        score -= 0.5
    else:
        signals.append("➡️ Normal volume")
    
    # Final recommendation
    if score >= 2:
        st.success("📈 **STRONG BUY** - Multiple bullish signals")
        confidence = min(score / 5 * 100, 95)
    elif score >= 0.5:
        st.success("📈 **BUY** - Bullish indicators")
        confidence = min(score / 5 * 100, 85)
    elif score >= -0.5:
        st.warning("➡️ **HOLD** - Mixed signals")
        confidence = 50
    elif score >= -2:
        st.error("📉 **SELL** - Bearish indicators")
        confidence = min(abs(score) / 5 * 100, 85)
    else:
        st.error("📉 **STRONG SELL** - Multiple bearish signals")
        confidence = min(abs(score) / 5 * 100, 95)
    
    st.write(f"**Confidence:** {confidence:.0f}% | **Score:** {score:.1f}/5")
    
    # Show all signals
    st.write("**Technical Analysis Details:**")
    for signal in signals:
        st.write(signal)
    
    # Statistics
    st.subheader("📊 Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        week_return = (data['Close'].iloc[-1] / data['Close'].iloc[-6] - 1) * 100
        st.metric("7-Day Return", f"{week_return:.1f}%")
    
    with col2:
        month_return = (data['Close'].iloc[-1] / data['Close'].iloc[-31] - 1) * 100
        st.metric("30-Day Return", f"{month_return:.1f}%")
    
    with col3:
        volatility = data['Close'].pct_change().rolling(window=20).std().iloc[-1] * 100
        st.metric("20-Day Volatility", f"{volatility:.1f}%")
    
    with col4:
        max_price = data['Close'].tail(90).max()
        min_price = data['Close'].tail(90).min()
        current_position = (latest_price - min_price) / (max_price - min_price) * 100
        st.metric("90-Day Range", f"{current_position:.0f}%")
    
    # Technical indicators chart
    st.subheader("📈 Technical Indicators")
    
    # RSI Chart
    st.write("**RSI (Relative Strength Index)**")
    rsi_chart = pd.DataFrame({
        'RSI': data['RSI'].tail(90),
    })
    st.line_chart(rsi_chart.dropna())
    
    # MACD Chart
    st.write("**MACD**")
    macd_chart = pd.DataFrame({
        'MACD': data['MACD'].tail(90),
        'Signal': data['MACD_Signal'].tail(90)
    })
    st.line_chart(macd_chart.dropna())
    
    # Data table
    st.subheader("📋 Recent Data")
    display_data = data[['Open', 'High', 'Low', 'Close', 'Volume']].tail(10)
    for col in ['Open', 'High', 'Low', 'Close']:
        display_data[col] = display_data[col].round(2)
    st.dataframe(display_data)

else:
    # Welcome message
    st.info("👈 Select a stock and click 'Analyze Stock' to see the analysis!")
    
    st.markdown("""
    ### 🚀 Features:
    - **Real-time stock data** via Alpha Vantage API
    - **Advanced technical analysis** (RSI, MACD, Bollinger Bands)
    - **AI-powered recommendations** with confidence scores
    - **Interactive charts** with multiple indicators
    - **Comprehensive statistics** and trend analysis
    
    ### 📊 Available Stocks:
    - **AAPL** - Apple Inc.
    - **TSLA** - Tesla Inc.
    - **GOOGL** - Alphabet Inc.
    - **MSFT** - Microsoft Corp.
    - **AMZN** - Amazon.com Inc.
    - **META** - Meta Platforms Inc.
    - **NVDA** - NVIDIA Corp.
    - **NFLX** - Netflix Inc.
    - **AMD** - Advanced Micro Devices
    - **INTC** - Intel Corp.
    
    ### 🔧 Setup:
    1. Get a free API key from [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
    2. Enter your API key in the sidebar
    3. Select a stock and click "Analyze Stock"
    
    ### 📈 Without API Key:
    - The app works with realistic sample data
    - Perfect for testing and demonstration
    - All analysis features are fully functional
    
    ### ⚠️ Disclaimer:
    This is for educational purposes only. Not financial advice.
    """)

# Footer
st.markdown("---")
st.markdown("**AI Stock Market Analyzer** | Powered by Alpha Vantage API")

# Sidebar info
st.sidebar.markdown("---")
if api_key:
    st.sidebar.success("✅ **API:** Connected")
else:
    st.sidebar.info("ℹ️ **API:** Demo Mode")
    st.sidebar.markdown("[Get Free API Key](https://www.alphavantage.co/support/#api-key)")

st.sidebar.markdown("🔧 **Version:** Real-time Data")