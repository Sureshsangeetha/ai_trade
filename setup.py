#!/usr/bin/env python3
"""
Setup script for AI Stock Market Technical Analysis & Investment Advisor
Helps users configure their environment and install dependencies.
"""

import os
import subprocess
import sys
import shutil

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required. Current version:", sys.version)
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def install_requirements():
    """Install required packages"""
    print("\n📦 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def setup_environment():
    """Set up environment variables"""
    print("\n⚙️ Setting up environment...")
    
    if not os.path.exists(".env.example"):
        print("❌ .env.example file not found")
        return False
    
    if not os.path.exists(".env"):
        shutil.copy(".env.example", ".env")
        print("✅ .env file created from template")
    else:
        print("⚠️ .env file already exists, skipping...")
    
    print("\n📝 Next steps:")
    print("1. Edit .env file with your API keys:")
    print("   - NewsAPI: https://newsapi.org/register")
    print("   - Finnhub: https://finnhub.io/register") 
    print("   - Twitter: https://developer.twitter.com/")
    print("2. Run: python demo_sentiment_analysis.py (to test)")
    print("3. Run: streamlit run app.py (to start the app)")
    
    return True

def test_imports():
    """Test if all required modules can be imported"""
    print("\n🧪 Testing imports...")
    required_modules = [
        "streamlit", "yfinance", "pandas", "numpy", "sklearn",
        "ta", "textblob", "vaderSentiment", "tweepy", "requests"
    ]
    
    failed_imports = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("Try running: pip install -r requirements.txt")
        return False
    
    print("\n✅ All modules imported successfully!")
    return True

def create_sample_env():
    """Create a sample .env file with instructions"""
    sample_content = """# AI Stock Market Analyzer - API Configuration
# Copy this file to .env and add your actual API keys

# NewsAPI - Get from https://newsapi.org/register
# Free tier: 1000 requests/month
NEWSAPI_KEY=your_newsapi_key_here

# Finnhub - Get from https://finnhub.io/register  
# Free tier: 60 calls/minute
FINNHUB_KEY=your_finnhub_key_here

# Twitter API v2 - Get from https://developer.twitter.com/
# Essential tier: Free
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here

# Optional settings
ENVIRONMENT=development
"""
    
    with open(".env.example", "w") as f:
        f.write(sample_content)
    print("✅ .env.example created")

def main():
    print("🚀 AI Stock Market Analyzer Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Create .env.example if it doesn't exist
    if not os.path.exists(".env.example"):
        create_sample_env()
    
    # Install requirements
    if not install_requirements():
        return 1
    
    # Test imports
    if not test_imports():
        return 1
    
    # Setup environment
    if not setup_environment():
        return 1
    
    print("\n🎉 Setup complete! Your AI Stock Market Analyzer is ready!")
    print("\n🔍 Quick start:")
    print("   python demo_sentiment_analysis.py  # Test sentiment analysis")
    print("   streamlit run app.py              # Start the web app")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())