import requests
import tweepy
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv
import os
from datetime import date, timedelta
import pandas as pd
import time
from typing import List, Dict, Optional

# Load environment variables
load_dotenv()

# API Keys - should be set in .env file
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "your_newsapi_key_here")
FINNHUB_KEY = os.getenv("FINNHUB_KEY", "your_finnhub_key_here")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "your_twitter_bearer_token_here")

# Initialize sentiment analyzers
vader_analyzer = SentimentIntensityAnalyzer()

class NewsAndSentimentAnalyzer:
    def __init__(self):
        self.twitter_client = None
        if TWITTER_BEARER_TOKEN != "your_twitter_bearer_token_here":
            try:
                self.twitter_client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
            except Exception as e:
                print(f"Twitter API setup failed: {e}")

    def fetch_newsapi_news(self, query: str = "stock market", days_back: int = 3) -> List[Dict]:
        """Fetch news from NewsAPI"""
        if NEWSAPI_KEY == "your_newsapi_key_here":
            return []
        
        try:
            from_date = (date.today() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            url = f"https://newsapi.org/v2/everything"
            params = {
                'q': query,
                'language': 'en',
                'pageSize': 20,
                'from': from_date,
                'sortBy': 'relevancy',
                'apiKey': NEWSAPI_KEY
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'ok':
                return data.get("articles", [])
            else:
                print(f"NewsAPI Error: {data.get('message', 'Unknown error')}")
                return []
                
        except Exception as e:
            print(f"Error fetching NewsAPI data: {e}")
            return []

    def fetch_finnhub_news(self, symbol: str = "AAPL", days_back: int = 3) -> List[Dict]:
        """Fetch company news from Finnhub"""
        if FINNHUB_KEY == "your_finnhub_key_here":
            return []
            
        try:
            today = date.today()
            from_date = today - timedelta(days=days_back)
            url = f"https://finnhub.io/api/v1/company-news"
            params = {
                'symbol': symbol.upper(),
                'from': from_date.strftime('%Y-%m-%d'),
                'to': today.strftime('%Y-%m-%d'),
                'token': FINNHUB_KEY
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            print(f"Error fetching Finnhub data: {e}")
            return []

    def fetch_twitter_sentiment(self, query: str, max_tweets: int = 50) -> List[Dict]:
        """Fetch tweets and analyze sentiment"""
        if not self.twitter_client:
            return []
            
        try:
            tweets = tweepy.Paginator(
                self.twitter_client.search_recent_tweets,
                query=f"{query} -is:retweet lang:en",
                max_results=min(max_tweets, 100),
                tweet_fields=['created_at', 'public_metrics', 'author_id']
            ).flatten(limit=max_tweets)
            
            twitter_data = []
            for tweet in tweets:
                sentiment_scores = self.analyze_sentiment_comprehensive(tweet.text)
                twitter_data.append({
                    'text': tweet.text,
                    'created_at': tweet.created_at,
                    'sentiment_compound': sentiment_scores['compound'],
                    'sentiment_label': sentiment_scores['label'],
                    'retweet_count': tweet.public_metrics.get('retweet_count', 0),
                    'like_count': tweet.public_metrics.get('like_count', 0)
                })
            
            return twitter_data
            
        except Exception as e:
            print(f"Error fetching Twitter data: {e}")
            return []

    def analyze_sentiment_comprehensive(self, text: str) -> Dict:
        """Analyze sentiment using multiple methods"""
        # TextBlob analysis
        blob = TextBlob(text)
        textblob_score = blob.sentiment.polarity
        
        # VADER analysis
        vader_scores = vader_analyzer.polarity_scores(text)
        
        # Combined sentiment score (weighted average)
        compound_score = (textblob_score + vader_scores['compound']) / 2
        
        # Determine sentiment label
        if compound_score >= 0.1:
            label = "Positive"
        elif compound_score <= -0.1:
            label = "Negative"
        else:
            label = "Neutral"
        
        return {
            'textblob': textblob_score,
            'vader': vader_scores['compound'],
            'compound': compound_score,
            'label': label,
            'confidence': abs(compound_score)
        }

    def get_comprehensive_sentiment_analysis(self, query: str, include_twitter: bool = True) -> Dict:
        """Get comprehensive sentiment analysis from all sources"""
        results = {
            'query': query,
            'timestamp': date.today().isoformat(),
            'news_articles': [],
            'twitter_sentiment': [],
            'overall_sentiment': {},
            'sentiment_summary': {}
        }
        
        # Fetch news from multiple sources
        newsapi_articles = self.fetch_newsapi_news(query)
        finnhub_articles = self.fetch_finnhub_news(query) if query.isupper() and len(query) <= 5 else []
        
        # Process NewsAPI articles
        for article in newsapi_articles:
            if article.get('title') and article.get('description'):
                text = f"{article['title']} {article['description']}"
                sentiment = self.analyze_sentiment_comprehensive(text)
                
                results['news_articles'].append({
                    'title': article['title'],
                    'description': article['description'],
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'url': article.get('url', ''),
                    'published_at': article.get('publishedAt', ''),
                    'sentiment': sentiment
                })
        
        # Process Finnhub articles
        for article in finnhub_articles:
            if article.get('headline') and article.get('summary'):
                text = f"{article['headline']} {article['summary']}"
                sentiment = self.analyze_sentiment_comprehensive(text)
                
                results['news_articles'].append({
                    'title': article['headline'],
                    'description': article['summary'],
                    'source': 'Finnhub',
                    'url': article.get('url', ''),
                    'published_at': article.get('datetime', ''),
                    'sentiment': sentiment
                })
        
        # Fetch Twitter sentiment if enabled
        if include_twitter:
            results['twitter_sentiment'] = self.fetch_twitter_sentiment(query)
        
        # Calculate overall sentiment
        all_sentiments = []
        
        # Add news sentiment scores
        for article in results['news_articles']:
            all_sentiments.append(article['sentiment']['compound'])
        
        # Add Twitter sentiment scores
        for tweet in results['twitter_sentiment']:
            all_sentiments.append(tweet['sentiment_compound'])
        
        if all_sentiments:
            avg_sentiment = sum(all_sentiments) / len(all_sentiments)
            results['overall_sentiment'] = {
                'average_score': avg_sentiment,
                'label': "Positive" if avg_sentiment > 0.1 else "Negative" if avg_sentiment < -0.1 else "Neutral",
                'confidence': abs(avg_sentiment),
                'total_sources': len(all_sentiments)
            }
            
            # Sentiment distribution
            positive_count = sum(1 for s in all_sentiments if s > 0.1)
            negative_count = sum(1 for s in all_sentiments if s < -0.1)
            neutral_count = len(all_sentiments) - positive_count - negative_count
            
            results['sentiment_summary'] = {
                'positive_percentage': (positive_count / len(all_sentiments)) * 100,
                'negative_percentage': (negative_count / len(all_sentiments)) * 100,
                'neutral_percentage': (neutral_count / len(all_sentiments)) * 100,
                'total_articles': len(results['news_articles']),
                'total_tweets': len(results['twitter_sentiment'])
            }
        
        return results

# Initialize the analyzer
analyzer = NewsAndSentimentAnalyzer()

# Backward compatibility functions
def get_news_with_sentiment(source="newsapi", query="stocks"):
    """Backward compatible function for existing code"""
    if source == "newsapi":
        articles = analyzer.fetch_newsapi_news(query)
        result = []
        for article in articles:
            if article.get('title'):
                text = f"{article.get('title', '')} {article.get('description', '')}"
                sentiment = analyzer.analyze_sentiment_comprehensive(text)
                result.append({
                    "title": article['title'],
                    "sentiment": sentiment['compound'],
                    "source": article.get('source', {}).get('name', '') if isinstance(article.get('source'), dict) else article.get('source', ''),
                    "url": article.get('url', '')
                })
        return result
    elif source == "finnhub":
        articles = analyzer.fetch_finnhub_news(query.upper() if query else "AAPL")
        result = []
        for article in articles:
            if article.get('headline'):
                text = f"{article.get('headline', '')} {article.get('summary', '')}"
                sentiment = analyzer.analyze_sentiment_comprehensive(text)
                result.append({
                    "title": article['headline'],
                    "sentiment": sentiment['compound'],
                    "source": "Finnhub",
                    "url": article.get('url', '')
                })
        return result
    else:
        return []

def analyze_sentiment(text):
    """Backward compatible sentiment analysis function"""
    return analyzer.analyze_sentiment_comprehensive(text)['compound']
