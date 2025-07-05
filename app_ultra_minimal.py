import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Page config
st.set_page_config(page_title="AI Stock Analyzer", layout="wide")

# Title
st.title("📈 AI Stock Market Analyzer")
st.write("**Demo Version** - Working with sample data")

# Sidebar
st.sidebar.header("📊 Stock Analysis")
symbol = st.sidebar.selectbox("Select Stock", ["AAPL", "TSLA", "GOOGL", "MSFT", "AMZN"])

# Generate sample data for demo
@st.cache_data
def generate_sample_data(symbol, days=365):
    """Generate realistic sample stock data"""
    np.random.seed(hash(symbol) % 1000)  # Different seed for each symbol
    
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    # Base prices for different stocks
    base_prices = {
        'AAPL': 150,
        'TSLA': 200,
        'GOOGL': 2500,
        'MSFT': 300,
        'AMZN': 3000
    }
    
    base_price = base_prices.get(symbol, 100)
    
    # Generate realistic price movements
    returns = np.random.normal(0.001, 0.02, days)  # Small daily returns with volatility
    prices = [base_price]
    
    for i in range(1, days):
        new_price = prices[-1] * (1 + returns[i])
        prices.append(max(new_price, 1))  # Ensure price stays positive
    
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

# Analysis button
analyze_btn = st.sidebar.button("🚀 Analyze Stock", type="primary")

if analyze_btn:
    # Generate sample data
    with st.spinner(f"Analyzing {symbol}..."):
        data = generate_sample_data(symbol)
    
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
    st.line_chart(data['Close'].tail(90))  # Last 90 days
    
    # Moving averages
    data['SMA_20'] = data['Close'].rolling(window=20).mean()
    data['SMA_50'] = data['Close'].rolling(window=50).mean()
    
    # Chart with moving averages
    st.subheader("📊 Price with Moving Averages")
    chart_data = pd.DataFrame({
        'Close': data['Close'],
        'SMA 20': data['SMA_20'],
        'SMA 50': data['SMA_50']
    })
    st.line_chart(chart_data.dropna().tail(90))
    
    # Simple AI Analysis
    st.subheader("🤖 AI Analysis")
    
    latest_price = latest['Close']
    sma_20 = data['SMA_20'].iloc[-1]
    sma_50 = data['SMA_50'].iloc[-1]
    
    signals = []
    score = 0
    
    if latest_price > sma_20:
        signals.append("✅ Price above 20-day average (Bullish)")
        score += 1
    else:
        signals.append("❌ Price below 20-day average (Bearish)")
    
    if latest_price > sma_50:
        signals.append("✅ Price above 50-day average (Bullish)")
        score += 1
    else:
        signals.append("❌ Price below 50-day average (Bearish)")
    
    if sma_20 > sma_50:
        signals.append("✅ Short-term trend positive")
        score += 1
    else:
        signals.append("❌ Short-term trend negative")
    
    # Volatility analysis
    volatility = data['Close'].pct_change().rolling(window=20).std().iloc[-1]
    avg_volatility = data['Close'].pct_change().rolling(window=20).std().mean()
    
    if volatility < avg_volatility:
        signals.append("✅ Low volatility (Stable)")
        score += 0.5
    else:
        signals.append("⚠️ High volatility (Risky)")
    
    # Prediction
    if score >= 2.5:
        st.success("📈 **BUY Signal** - Strong bullish indicators")
        confidence = min(score / 3 * 100, 90)
        st.write(f"**Confidence:** {confidence:.0f}%")
    elif score >= 1.5:
        st.warning("➡️ **HOLD** - Mixed signals")
        confidence = 50
        st.write(f"**Confidence:** {confidence:.0f}%")
    else:
        st.error("📉 **SELL Signal** - Bearish indicators")
        confidence = min((3 - score) / 3 * 100, 90)
        st.write(f"**Confidence:** {confidence:.0f}%")
    
    # Show signals
    st.write("**Analysis Details:**")
    for signal in signals:
        st.write(signal)
    
    # Statistics
    st.subheader("📊 Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        returns = data['Close'].pct_change().dropna()
        st.metric("30-Day Return", f"{(data['Close'].iloc[-1] / data['Close'].iloc[-31] - 1) * 100:.1f}%")
    
    with col2:
        st.metric("Volatility", f"{volatility * 100:.1f}%")
    
    with col3:
        max_price = data['Close'].tail(90).max()
        min_price = data['Close'].tail(90).min()
        current_position = (latest_price - min_price) / (max_price - min_price) * 100
        st.metric("90-Day Position", f"{current_position:.0f}%")
    
    # Data table
    st.subheader("📋 Recent Data")
    display_data = data[['Open', 'High', 'Low', 'Close', 'Volume']].tail(10)
    display_data['Close'] = display_data['Close'].round(2)
    display_data['Open'] = display_data['Open'].round(2)
    display_data['High'] = display_data['High'].round(2)
    display_data['Low'] = display_data['Low'].round(2)
    st.dataframe(display_data)

else:
    # Welcome message
    st.info("👈 Select a stock and click 'Analyze Stock' to see the analysis!")
    
    st.markdown("""
    ### 🚀 Demo Features:
    - **Sample stock data** for major companies
    - **Price charts** with technical indicators  
    - **AI analysis** with buy/sell/hold recommendations
    - **Moving averages** (20-day and 50-day)
    - **Volatility analysis** and risk assessment
    - **Technical signals** and trend analysis
    
    ### 📊 Available Stocks:
    - **AAPL** - Apple Inc.
    - **TSLA** - Tesla Inc.
    - **GOOGL** - Alphabet Inc.
    - **MSFT** - Microsoft Corp.
    - **AMZN** - Amazon.com Inc.
    
    ### 🔧 How it works:
    1. Select a stock from the dropdown
    2. Click "Analyze Stock"
    3. View comprehensive analysis and charts
    
    ### ⚠️ Note:
    This demo uses simulated data. For real-time data, the full version connects to Yahoo Finance API.
    
    ### ⚠️ Disclaimer:
    This is for educational purposes only. Not financial advice.
    """)

# Footer
st.markdown("---")
st.markdown("**AI Stock Market Analyzer** | Demo Version | Educational Use Only")

# Status info
st.sidebar.markdown("---")
st.sidebar.info("📊 **Demo Mode**\nUsing sample data for demonstration")
st.sidebar.success("✅ **Status:** Fully Operational")
st.sidebar.markdown("🔧 **Next:** Add real-time data API")