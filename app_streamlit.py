import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import base64
import os

# Essential technical analysis imports
try:
    from ta.trend import SMAIndicator, EMAIndicator, MACD, ADXIndicator
    from ta.volatility import BollingerBands
    from ta.momentum import RSIIndicator, StochasticOscillator
    TA_AVAILABLE = True
except ImportError:
    st.warning("Technical analysis library not available. Basic functionality will be limited.")
    TA_AVAILABLE = False

# Machine learning imports
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    ML_AVAILABLE = True
except ImportError:
    st.warning("Machine learning features not available.")
    ML_AVAILABLE = False

# --- Helper Functions ---
def fetch_data(symbol, start, end, interval="1d"):
    """Fetch stock data from Yahoo Finance"""
    try:
        data = yf.download(symbol, start=start, end=end, interval=interval)
        if data.empty:
            return pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume'])
        return data
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume'])

def add_basic_indicators(df):
    """Add basic technical indicators"""
    if not TA_AVAILABLE or df.empty:
        return df
    
    try:
        close = df['Close']
        
        # Moving averages
        df['SMA20'] = SMAIndicator(close, window=20).sma_indicator()
        df['SMA50'] = SMAIndicator(close, window=50).sma_indicator()
        df['EMA20'] = EMAIndicator(close, window=20).ema_indicator()
        
        # RSI
        df['RSI'] = RSIIndicator(close, window=14).rsi()
        
        # MACD
        macd = MACD(close)
        df['MACD'] = macd.macd()
        df['MACD_signal'] = macd.macd_signal()
        
        # Bollinger Bands
        bb = BollingerBands(close, window=20, window_dev=2)
        df['BB_High'] = bb.bollinger_hband()
        df['BB_Low'] = bb.bollinger_lband()
        
        # Basic returns
        df['Daily_Return'] = close.pct_change()
        df['Volatility_20'] = close.pct_change().rolling(window=20).std()
        
    except Exception as e:
        st.warning(f"Error calculating indicators: {e}")
    
    return df

def simple_prediction(df):
    """Simple prediction based on technical indicators"""
    if df.empty or len(df) < 50:
        return None, "Insufficient data"
    
    try:
        latest = df.iloc[-1]
        
        # Simple scoring system
        score = 0
        signals = []
        
        # Price vs Moving Averages
        if latest['Close'] > latest['SMA20']:
            score += 1
            signals.append("Price above SMA20")
        if latest['Close'] > latest['SMA50']:
            score += 1
            signals.append("Price above SMA50")
            
        # RSI
        if 30 <= latest['RSI'] <= 70:
            score += 1
            signals.append("RSI in normal range")
        elif latest['RSI'] < 30:
            score += 2
            signals.append("RSI oversold (bullish)")
            
        # MACD
        if latest['MACD'] > latest['MACD_signal']:
            score += 1
            signals.append("MACD bullish")
            
        # Recent volatility
        if latest['Volatility_20'] < df['Volatility_20'].mean():
            score += 1
            signals.append("Low volatility")
            
        # Simple prediction
        if score >= 4:
            prediction = "BUY"
            confidence = min(score / 6, 1.0)
        elif score <= 2:
            prediction = "SELL"
            confidence = min((6 - score) / 6, 1.0)
        else:
            prediction = "HOLD"
            confidence = 0.5
            
        return {
            'prediction': prediction,
            'confidence': confidence,
            'score': score,
            'signals': signals
        }, None
        
    except Exception as e:
        return None, f"Prediction error: {e}"

# --- Streamlit App ---
st.set_page_config(page_title="AI Stock Market Analyzer", layout="wide")
st.title("📈 AI Stock Market Technical Analysis")

# Sidebar inputs
st.sidebar.header("Stock Analysis Settings")
symbol = st.sidebar.text_input("Stock Symbol", value="AAPL")
today = datetime.date.today()
default_start = today - datetime.timedelta(days=365)
start_date = st.sidebar.date_input("Start Date", default_start)
end_date = st.sidebar.date_input("End Date", today)
interval = st.sidebar.selectbox("Interval", ["1d", "1h", "30m", "15m", "5m"], index=0)

# Main analysis
if st.sidebar.button("📊 Analyze Stock", type="primary"):
    with st.spinner(f'Analyzing {symbol}...'):
        # Fetch data
        df = fetch_data(symbol, start_date, end_date, interval)
        
        if df.empty:
            st.error(f"No data found for {symbol}. Please check the symbol and try again.")
        else:
            # Add indicators
            df = add_basic_indicators(df)
            
            # Display current price info
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                price_change = latest['Close'] - prev['Close']
                price_change_pct = (price_change / prev['Close']) * 100
                st.metric(
                    "Current Price", 
                    f"${latest['Close']:.2f}",
                    f"{price_change:+.2f} ({price_change_pct:+.2f}%)"
                )
            
            with col2:
                st.metric("Volume", f"{latest['Volume']:,.0f}")
            
            with col3:
                if 'RSI' in df.columns:
                    st.metric("RSI", f"{latest['RSI']:.1f}")
                else:
                    st.metric("High", f"${latest['High']:.2f}")
            
            with col4:
                if 'Volatility_20' in df.columns:
                    st.metric("20-Day Volatility", f"{latest['Volatility_20']:.3f}")
                else:
                    st.metric("Low", f"${latest['Low']:.2f}")
            
            # Price chart
            st.subheader("📈 Price Chart")
            
            # Create chart data
            chart_data = pd.DataFrame()
            chart_data['Close'] = df['Close']
            
            if 'SMA20' in df.columns:
                chart_data['SMA20'] = df['SMA20']
            if 'SMA50' in df.columns:
                chart_data['SMA50'] = df['SMA50']
            
            st.line_chart(chart_data.dropna())
            
            # Technical indicators
            if TA_AVAILABLE and any(col in df.columns for col in ['RSI', 'MACD']):
                st.subheader("🔧 Technical Indicators")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'RSI' in df.columns:
                        st.markdown("**RSI (Relative Strength Index)**")
                        rsi_data = pd.DataFrame({'RSI': df['RSI']})
                        st.line_chart(rsi_data.dropna())
                
                with col2:
                    if all(col in df.columns for col in ['MACD', 'MACD_signal']):
                        st.markdown("**MACD**")
                        macd_data = pd.DataFrame({
                            'MACD': df['MACD'],
                            'Signal': df['MACD_signal']
                        })
                        st.line_chart(macd_data.dropna())
            
            # Simple prediction
            st.subheader("🤖 AI Analysis")
            prediction_result, error = simple_prediction(df)
            
            if error:
                st.error(error)
            elif prediction_result:
                pred = prediction_result['prediction']
                conf = prediction_result['confidence']
                
                # Display prediction with color coding
                if pred == "BUY":
                    st.success(f"📈 **{pred}** - Confidence: {conf:.1%}")
                elif pred == "SELL":
                    st.error(f"📉 **{pred}** - Confidence: {conf:.1%}")
                else:
                    st.warning(f"➡️ **{pred}** - Confidence: {conf:.1%}")
                
                # Show signals
                st.markdown("**Analysis Signals:**")
                for signal in prediction_result['signals']:
                    st.write(f"• {signal}")
            
            # Data table
            st.subheader("📋 Recent Data")
            display_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            if 'SMA20' in df.columns:
                display_columns.extend(['SMA20', 'RSI', 'MACD'])
            
            available_columns = [col for col in display_columns if col in df.columns]
            st.dataframe(df[available_columns].tail(10), use_container_width=True)
            
            # Download data
            csv = df.to_csv(index=True)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="{symbol}_data.csv">📥 Download Data as CSV</a>'
            st.markdown(href, unsafe_allow_html=True)

else:
    # Welcome message
    st.info("👈 Enter a stock symbol in the sidebar and click 'Analyze Stock' to get started!")
    
    st.markdown("""
    ### 🚀 Features Available:
    - **Real-time stock data** from Yahoo Finance
    - **Technical indicators** (SMA, EMA, RSI, MACD, Bollinger Bands)
    - **AI-powered analysis** with buy/sell/hold recommendations
    - **Interactive charts** and data visualization
    - **Data export** functionality
    
    ### 📊 How to Use:
    1. Enter a stock symbol (e.g., AAPL, TSLA, GOOGL)
    2. Select your preferred date range
    3. Choose the data interval
    4. Click "Analyze Stock" to see the results
    
    ### ⚠️ Disclaimer:
    This tool is for educational purposes only. Always do your own research and consult with financial professionals before making investment decisions.
    """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>AI Stock Market Analyzer | Built with Streamlit | Not Financial Advice</p>
    </div>
    """, 
    unsafe_allow_html=True
)

# Add some custom CSS
st.markdown("""
<style>
.stButton > button {
    background-color: #4CAF50;
    color: white;
    border-radius: 5px;
}
.stSelectbox > div > div {
    background-color: #f0f2f6;
}
</style>
""", unsafe_allow_html=True)