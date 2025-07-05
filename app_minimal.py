import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Page config
st.set_page_config(page_title="AI Stock Analyzer", layout="wide")

# Title
st.title("📈 AI Stock Market Analyzer")

# Sidebar
st.sidebar.header("📊 Stock Analysis")
symbol = st.sidebar.text_input("Stock Symbol", value="AAPL", help="Enter a stock symbol (e.g., AAPL, TSLA)")

# Date inputs
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=365))
with col2:
    end_date = st.date_input("End Date", value=datetime.now())

# Analysis button
analyze_btn = st.sidebar.button("🚀 Analyze Stock", type="primary")

if analyze_btn and symbol:
    try:
        # Fetch data
        with st.spinner(f"Fetching data for {symbol}..."):
            data = yf.download(symbol, start=start_date, end=end_date)
        
        if data.empty:
            st.error(f"No data found for {symbol}. Please check the symbol.")
        else:
            # Latest price info
            latest = data.iloc[-1]
            prev = data.iloc[-2] if len(data) > 1 else latest
            
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
            st.line_chart(data['Close'])
            
            # Simple moving averages
            data['SMA_20'] = data['Close'].rolling(window=20).mean()
            data['SMA_50'] = data['Close'].rolling(window=50).mean()
            
            # Chart with moving averages
            st.subheader("📊 Price with Moving Averages")
            chart_data = pd.DataFrame({
                'Close': data['Close'],
                'SMA 20': data['SMA_20'],
                'SMA 50': data['SMA_50']
            })
            st.line_chart(chart_data.dropna())
            
            # Simple AI Analysis
            st.subheader("🤖 Simple AI Analysis")
            
            latest_price = latest['Close']
            sma_20 = data['SMA_20'].iloc[-1] if not pd.isna(data['SMA_20'].iloc[-1]) else latest_price
            sma_50 = data['SMA_50'].iloc[-1] if not pd.isna(data['SMA_50'].iloc[-1]) else latest_price
            
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
            
            # Prediction
            if score >= 2:
                st.success("📈 **BUY Signal** - Bullish indicators detected")
            elif score == 1:
                st.warning("➡️ **HOLD** - Mixed signals")
            else:
                st.error("📉 **SELL Signal** - Bearish indicators detected")
            
            # Show signals
            st.write("**Analysis Details:**")
            for signal in signals:
                st.write(signal)
            
            # Data table
            st.subheader("📋 Recent Data")
            st.dataframe(data[['Open', 'High', 'Low', 'Close', 'Volume']].tail(10))
            
    except Exception as e:
        st.error(f"Error analyzing {symbol}: {str(e)}")

elif not symbol:
    st.info("👈 Enter a stock symbol in the sidebar to get started!")

else:
    # Welcome message
    st.info("👈 Click 'Analyze Stock' to see real-time analysis!")
    
    st.markdown("""
    ### 🚀 Features:
    - **Real-time stock data** from Yahoo Finance
    - **Price charts** with technical indicators  
    - **AI analysis** with buy/sell recommendations
    - **Moving averages** (20-day and 50-day)
    - **Technical signals** and trend analysis
    
    ### 📊 How to use:
    1. Enter a stock symbol (e.g., AAPL, TSLA, GOOGL)
    2. Select your date range
    3. Click "Analyze Stock"
    
    ### ⚠️ Disclaimer:
    This is for educational purposes only. Not financial advice.
    """)

# Footer
st.markdown("---")
st.markdown("**AI Stock Market Analyzer** | Built with Streamlit | Educational Use Only")