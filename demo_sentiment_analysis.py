#!/usr/bin/env python3
"""
Demo script showing how to use the enhanced news and sentiment analysis features.
Run this script to see comprehensive sentiment analysis in action.
"""

import os
import json
from news_sentiment import NewsAndSentimentAnalyzer

def main():
    print("🚀 AI Stock Market Sentiment Analysis Demo")
    print("=" * 50)
    
    # Initialize the analyzer
    analyzer = NewsAndSentimentAnalyzer()
    
    # Check API status
    print("\n📊 API Status Check:")
    print(f"NewsAPI: {'✅ Configured' if analyzer.NEWSAPI_KEY != 'your_newsapi_key_here' else '❌ Not configured'}")
    print(f"Finnhub: {'✅ Configured' if analyzer.FINNHUB_KEY != 'your_finnhub_key_here' else '❌ Not configured'}")
    print(f"Twitter: {'✅ Configured' if analyzer.twitter_client else '❌ Not configured'}")
    
    # Demo companies for analysis
    demo_symbols = ["AAPL", "TSLA", "MSFT", "GOOGL", "AMZN"]
    
    print(f"\n🔍 Running sentiment analysis for: {', '.join(demo_symbols)}")
    print("-" * 50)
    
    for symbol in demo_symbols:
        print(f"\n📈 Analyzing {symbol}...")
        
        try:
            # Get comprehensive sentiment analysis
            results = analyzer.get_comprehensive_sentiment_analysis(
                query=symbol, 
                include_twitter=True
            )
            
            if results['overall_sentiment']:
                sentiment = results['overall_sentiment']
                summary = results['sentiment_summary']
                
                print(f"Overall Sentiment: {sentiment['label']} ({sentiment['average_score']:.3f})")
                print(f"Confidence: {sentiment['confidence']:.1%}")
                print(f"Sources: {summary['total_articles']} articles, {summary['total_tweets']} tweets")
                print(f"Distribution: {summary['positive_percentage']:.1f}% positive, "
                      f"{summary['negative_percentage']:.1f}% negative, "
                      f"{summary['neutral_percentage']:.1f}% neutral")
                
                # Show top sentiment article if available
                if results['news_articles']:
                    top_article = max(results['news_articles'], 
                                    key=lambda x: abs(x['sentiment']['compound']))
                    print(f"Top Article: {top_article['title'][:60]}...")
                    print(f"Article Sentiment: {top_article['sentiment']['label']} ({top_article['sentiment']['compound']:.3f})")
                
            else:
                print("❌ No sentiment data available (check API keys)")
                
        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {e}")
    
    print(f"\n💡 Demo complete! To run the full app: streamlit run app.py")
    print("\n📚 Setup instructions:")
    print("1. Copy .env.example to .env")
    print("2. Add your API keys to .env file")
    print("3. Run: pip install -r requirements.txt")
    print("4. Start the app: streamlit run app.py")

if __name__ == "__main__":
    main()