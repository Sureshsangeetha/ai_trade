import requests
from textblob import TextBlob
from dotenv import load_dotenv
import os
from datetime import date, timedelta

load_dotenv()
NEWSAPI_KEY = os.getenv("7d6403a5ede143aba79b36fc1df11fbd")
FINNHUB_KEY = os.getenv("d1k251hr01ql1h3a6jo0d1k251hr01ql1h3a6jog")

# ---------- NewsAPI Function ----------
def fetch_newsapi_news(query="stock market"):
    url = f"https://newsapi.org/v2/everything?q={query}&language=en&pageSize=5&apiKey={NEWSAPI_KEY}"
    response = requests.get(url)
    data = response.json()
    return data.get("articles", [])

# ---------- Finnhub Function ----------
def fetch_finnhub_news(symbol="AAPL"):
    today = date.today()
    from_date = today - timedelta(days=3)
    url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from={from_date}&to={today}&token={FINNHUB_KEY}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return []

# ---------- Sentiment Analysis ----------
def analyze_sentiment(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity  # Range: -1 (negative) to 1 (positive)

# ---------- Combine and Display ----------
def get_news_with_sentiment(source="newsapi", query="stocks"):
    if source == "newsapi":
        articles = fetch_newsapi_news(query)
    elif source == "finnhub":
        articles = fetch_finnhub_news(query.upper())
    else:
        return []

    result = []
    for article in articles:
        title = article.get("title", "")
        description = article.get("description", "")
        sentiment = analyze_sentiment(f"{title} {description}")
        result.append({
            "title": title,
            "sentiment": sentiment,
            "source": article.get("source", {}).get("name", "") if isinstance(article.get("source"), dict) else article.get("source", ""),
            "url": article.get("url", "")
        })
    return result
