#!/usr/bin/env python3
"""
Test script to verify app functionality before deployment.
"""

import sys
import importlib

def test_imports():
    """Test if all required packages can be imported"""
    print("🧪 Testing Package Imports...")
    
    required_packages = [
        'streamlit',
        'yfinance', 
        'pandas',
        'numpy',
        'ta',
        'sklearn',
        'matplotlib',
        'seaborn',
        'plotly'
    ]
    
    failed_imports = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            failed_imports.append(package)
    
    return failed_imports

def test_data_fetch():
    """Test if data fetching works"""
    print("\n📊 Testing Data Fetch...")
    
    try:
        import yfinance as yf
        import pandas as pd
        from datetime import datetime, timedelta
        
        # Test fetching Apple stock data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        data = yf.download('AAPL', start=start_date, end=end_date)
        
        if not data.empty:
            print(f"✅ Successfully fetched {len(data)} days of AAPL data")
            print(f"   Latest close: ${data['Close'].iloc[-1]:.2f}")
            return True
        else:
            print("❌ No data returned")
            return False
            
    except Exception as e:
        print(f"❌ Data fetch failed: {e}")
        return False

def test_technical_analysis():
    """Test technical analysis calculations"""
    print("\n🔧 Testing Technical Analysis...")
    
    try:
        from ta.trend import SMAIndicator
        import pandas as pd
        import numpy as np
        
        # Create sample data
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        prices = 100 + np.cumsum(np.random.randn(100) * 0.01)
        
        df = pd.DataFrame({'Close': prices}, index=dates)
        
        # Test SMA calculation
        sma = SMAIndicator(df['Close'], window=20)
        df['SMA20'] = sma.sma_indicator()
        
        if not df['SMA20'].isna().all():
            print("✅ Technical analysis calculations working")
            return True
        else:
            print("❌ Technical analysis failed")
            return False
            
    except Exception as e:
        print(f"❌ Technical analysis test failed: {e}")
        return False

def main():
    print("🧪 AI Stock Market Analyzer - Test Suite")
    print("=" * 50)
    
    # Test imports
    failed_imports = test_imports()
    
    if failed_imports:
        print(f"\n❌ Missing packages: {', '.join(failed_imports)}")
        print("Install them with: pip install -r requirements.txt")
        return False
    
    # Test data fetching
    if not test_data_fetch():
        print("\n❌ Data fetching test failed")
        return False
    
    # Test technical analysis
    if not test_technical_analysis():
        print("\n❌ Technical analysis test failed")
        return False
    
    print("\n🎉 All tests passed!")
    print("\n✅ Your app should work correctly on Streamlit Cloud")
    print("\nTo deploy:")
    print("1. Commit your code: git add . && git commit -m 'Ready for deployment'")
    print("2. Push to GitHub: git push origin main")
    print("3. Deploy on Streamlit Cloud")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)