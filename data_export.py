#!/usr/bin/env python3
"""
Data Export and Reporting Module for AI Stock Market Analyzer
Provides functionality to export sentiment analysis data and generate professional reports.
"""

import os
import json
import csv
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass, asdict
from news_sentiment import NewsAndSentimentAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SentimentRecord:
    """Data class for sentiment analysis records"""
    symbol: str
    timestamp: str
    sentiment_score: float
    sentiment_label: str
    confidence: float
    news_articles_count: int
    tweets_count: int
    positive_percentage: float
    negative_percentage: float
    neutral_percentage: float
    source: str = "comprehensive"
    
class DataExporter:
    """Handles data export and reporting functionality"""
    
    def __init__(self, db_path: str = "sentiment_data.db"):
        self.db_path = db_path
        self.analyzer = NewsAndSentimentAnalyzer()
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for storing sentiment data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sentiment_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    sentiment_score REAL NOT NULL,
                    sentiment_label TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    news_articles_count INTEGER NOT NULL,
                    tweets_count INTEGER NOT NULL,
                    positive_percentage REAL NOT NULL,
                    negative_percentage REAL NOT NULL,
                    neutral_percentage REAL NOT NULL,
                    source TEXT NOT NULL DEFAULT 'comprehensive',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_symbol_timestamp 
                ON sentiment_records(symbol, timestamp)
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    def store_sentiment_data(self, symbol: str, analysis_results: Dict):
        """Store sentiment analysis results in database"""
        if not analysis_results.get('overall_sentiment'):
            return False
        
        try:
            record = SentimentRecord(
                symbol=symbol,
                timestamp=datetime.now().isoformat(),
                sentiment_score=analysis_results['overall_sentiment']['average_score'],
                sentiment_label=analysis_results['overall_sentiment']['label'],
                confidence=analysis_results['overall_sentiment']['confidence'],
                news_articles_count=analysis_results['sentiment_summary']['total_articles'],
                tweets_count=analysis_results['sentiment_summary']['total_tweets'],
                positive_percentage=analysis_results['sentiment_summary']['positive_percentage'],
                negative_percentage=analysis_results['sentiment_summary']['negative_percentage'],
                neutral_percentage=analysis_results['sentiment_summary']['neutral_percentage']
            )
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sentiment_records (
                    symbol, timestamp, sentiment_score, sentiment_label, confidence,
                    news_articles_count, tweets_count, positive_percentage,
                    negative_percentage, neutral_percentage, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.symbol, record.timestamp, record.sentiment_score,
                record.sentiment_label, record.confidence, record.news_articles_count,
                record.tweets_count, record.positive_percentage,
                record.negative_percentage, record.neutral_percentage, record.source
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Stored sentiment data for {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing sentiment data: {e}")
            return False
    
    def get_sentiment_history(self, symbol: str, days: int = 30) -> List[SentimentRecord]:
        """Retrieve sentiment history for a symbol"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            cursor.execute('''
                SELECT symbol, timestamp, sentiment_score, sentiment_label, confidence,
                       news_articles_count, tweets_count, positive_percentage,
                       negative_percentage, neutral_percentage, source
                FROM sentiment_records
                WHERE symbol = ? AND timestamp >= ?
                ORDER BY timestamp DESC
            ''', (symbol, start_date))
            
            records = []
            for row in cursor.fetchall():
                records.append(SentimentRecord(*row))
            
            conn.close()
            return records
            
        except Exception as e:
            logger.error(f"Error retrieving sentiment history: {e}")
            return []
    
    def export_to_csv(self, symbol: str, days: int = 30, filename: str = None) -> str:
        """Export sentiment data to CSV format"""
        records = self.get_sentiment_history(symbol, days)
        
        if not filename:
            filename = f"sentiment_data_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'symbol', 'timestamp', 'sentiment_score', 'sentiment_label', 
                    'confidence', 'news_articles_count', 'tweets_count',
                    'positive_percentage', 'negative_percentage', 'neutral_percentage', 'source'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for record in records:
                    writer.writerow(asdict(record))
            
            logger.info(f"Exported {len(records)} records to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return None
    
    def export_to_json(self, symbol: str, days: int = 30, filename: str = None) -> str:
        """Export sentiment data to JSON format"""
        records = self.get_sentiment_history(symbol, days)
        
        if not filename:
            filename = f"sentiment_data_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            export_data = {
                'export_info': {
                    'symbol': symbol,
                    'export_date': datetime.now().isoformat(),
                    'days_included': days,
                    'total_records': len(records)
                },
                'records': [asdict(record) for record in records]
            }
            
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(records)} records to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            return None
    
    def generate_html_report(self, symbol: str, days: int = 30, filename: str = None) -> str:
        """Generate an HTML report with sentiment analysis"""
        records = self.get_sentiment_history(symbol, days)
        
        if not filename:
            filename = f"sentiment_report_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        try:
            # Calculate statistics
            if records:
                sentiment_scores = [r.sentiment_score for r in records]
                avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
                max_sentiment = max(sentiment_scores)
                min_sentiment = min(sentiment_scores)
                
                positive_count = sum(1 for r in records if r.sentiment_label == 'Positive')
                negative_count = sum(1 for r in records if r.sentiment_label == 'Negative')
                neutral_count = sum(1 for r in records if r.sentiment_label == 'Neutral')
                
                total_articles = sum(r.news_articles_count for r in records)
                total_tweets = sum(r.tweets_count for r in records)
            else:
                avg_sentiment = max_sentiment = min_sentiment = 0
                positive_count = negative_count = neutral_count = 0
                total_articles = total_tweets = 0
            
            # Generate HTML content
            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Sentiment Analysis Report - {symbol}</title>
                <style>
                    body {{
                        font-family: 'Arial', sans-serif;
                        margin: 0;
                        padding: 20px;
                        background-color: #f5f5f5;
                    }}
                    .container {{
                        max-width: 1200px;
                        margin: 0 auto;
                        background-color: white;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        text-align: center;
                        margin-bottom: 30px;
                        border-bottom: 2px solid #007bff;
                        padding-bottom: 20px;
                    }}
                    .stats-grid {{
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                        gap: 20px;
                        margin-bottom: 30px;
                    }}
                    .stat-card {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 20px;
                        border-radius: 10px;
                        text-align: center;
                    }}
                    .stat-value {{
                        font-size: 2em;
                        font-weight: bold;
                        margin-bottom: 5px;
                    }}
                    .stat-label {{
                        font-size: 0.9em;
                        opacity: 0.9;
                    }}
                    .records-table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin-top: 20px;
                    }}
                    .records-table th, .records-table td {{
                        border: 1px solid #ddd;
                        padding: 12px;
                        text-align: left;
                    }}
                    .records-table th {{
                        background-color: #f8f9fa;
                        font-weight: bold;
                    }}
                    .positive {{ color: #28a745; }}
                    .negative {{ color: #dc3545; }}
                    .neutral {{ color: #ffc107; }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #ddd;
                        color: #666;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>📊 Sentiment Analysis Report</h1>
                        <h2>{symbol}</h2>
                        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                        <p>Analysis Period: {days} days</p>
                    </div>
                    
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-value">{len(records)}</div>
                            <div class="stat-label">Total Records</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{avg_sentiment:.3f}</div>
                            <div class="stat-label">Average Sentiment</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{positive_count}</div>
                            <div class="stat-label">Positive Records</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{negative_count}</div>
                            <div class="stat-label">Negative Records</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{total_articles}</div>
                            <div class="stat-label">Total Articles</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{total_tweets}</div>
                            <div class="stat-label">Total Tweets</div>
                        </div>
                    </div>
                    
                    <h3>📈 Sentiment History</h3>
                    <table class="records-table">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Sentiment</th>
                                <th>Score</th>
                                <th>Confidence</th>
                                <th>Articles</th>
                                <th>Tweets</th>
                                <th>Positive %</th>
                                <th>Negative %</th>
                            </tr>
                        </thead>
                        <tbody>
            """
            
            # Add records to table
            for record in records:
                sentiment_class = record.sentiment_label.lower()
                html_content += f"""
                            <tr>
                                <td>{record.timestamp[:19]}</td>
                                <td class="{sentiment_class}">{record.sentiment_label}</td>
                                <td>{record.sentiment_score:.3f}</td>
                                <td>{record.confidence:.1%}</td>
                                <td>{record.news_articles_count}</td>
                                <td>{record.tweets_count}</td>
                                <td>{record.positive_percentage:.1f}%</td>
                                <td>{record.negative_percentage:.1f}%</td>
                            </tr>
                """
            
            html_content += """
                        </tbody>
                    </table>
                    
                    <div class="footer">
                        <p>Generated by AI Stock Market Analyzer</p>
                        <p>⚠️ This analysis is for educational purposes only and should not be used as financial advice.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            with open(filename, 'w', encoding='utf-8') as htmlfile:
                htmlfile.write(html_content)
            
            logger.info(f"Generated HTML report: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error generating HTML report: {e}")
            return None
    
    def bulk_analysis_and_export(self, symbols: List[str], export_format: str = 'csv'):
        """Perform bulk analysis and export for multiple symbols"""
        results = {}
        
        for symbol in symbols:
            try:
                logger.info(f"Analyzing {symbol}...")
                analysis_results = self.analyzer.get_comprehensive_sentiment_analysis(symbol)
                
                if analysis_results.get('overall_sentiment'):
                    # Store in database
                    self.store_sentiment_data(symbol, analysis_results)
                    
                    # Export data
                    if export_format.lower() == 'csv':
                        filename = self.export_to_csv(symbol, days=7)
                    elif export_format.lower() == 'json':
                        filename = self.export_to_json(symbol, days=7)
                    elif export_format.lower() == 'html':
                        filename = self.generate_html_report(symbol, days=7)
                    else:
                        filename = None
                    
                    results[symbol] = {
                        'status': 'success',
                        'sentiment': analysis_results['overall_sentiment'],
                        'filename': filename
                    }
                else:
                    results[symbol] = {
                        'status': 'failed',
                        'error': 'No sentiment data available'
                    }
                    
            except Exception as e:
                results[symbol] = {
                    'status': 'error',
                    'error': str(e)
                }
                logger.error(f"Error analyzing {symbol}: {e}")
        
        return results
    
    def get_database_stats(self) -> Dict:
        """Get statistics about stored data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total records
            cursor.execute("SELECT COUNT(*) FROM sentiment_records")
            total_records = cursor.fetchone()[0]
            
            # Unique symbols
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM sentiment_records")
            unique_symbols = cursor.fetchone()[0]
            
            # Date range
            cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM sentiment_records")
            date_range = cursor.fetchone()
            
            # Top symbols by record count
            cursor.execute("""
                SELECT symbol, COUNT(*) as count 
                FROM sentiment_records 
                GROUP BY symbol 
                ORDER BY count DESC 
                LIMIT 10
            """)
            top_symbols = cursor.fetchall()
            
            conn.close()
            
            return {
                'total_records': total_records,
                'unique_symbols': unique_symbols,
                'date_range': {
                    'earliest': date_range[0],
                    'latest': date_range[1]
                },
                'top_symbols': [{'symbol': sym, 'count': count} for sym, count in top_symbols]
            }
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}

# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Data Export and Reporting Tool")
    parser.add_argument('--analyze', metavar='SYMBOL', help='Analyze and store sentiment for symbol')
    parser.add_argument('--export', nargs=2, metavar=('SYMBOL', 'FORMAT'), 
                       help='Export data for symbol in format (csv/json/html)')
    parser.add_argument('--bulk', nargs='+', metavar='SYMBOLS', 
                       help='Bulk analyze multiple symbols')
    parser.add_argument('--report', metavar='SYMBOL', help='Generate HTML report for symbol')
    parser.add_argument('--stats', action='store_true', help='Show database statistics')
    parser.add_argument('--days', type=int, default=30, help='Number of days for analysis')
    
    args = parser.parse_args()
    
    exporter = DataExporter()
    
    if args.analyze:
        logger.info(f"Analyzing {args.analyze}...")
        results = exporter.analyzer.get_comprehensive_sentiment_analysis(args.analyze)
        if results.get('overall_sentiment'):
            exporter.store_sentiment_data(args.analyze, results)
            print(f"✅ Analysis complete for {args.analyze}")
        else:
            print(f"❌ No sentiment data available for {args.analyze}")
    
    elif args.export:
        symbol, format_type = args.export
        logger.info(f"Exporting {symbol} data in {format_type} format...")
        
        if format_type.lower() == 'csv':
            filename = exporter.export_to_csv(symbol, args.days)
        elif format_type.lower() == 'json':
            filename = exporter.export_to_json(symbol, args.days)
        elif format_type.lower() == 'html':
            filename = exporter.generate_html_report(symbol, args.days)
        else:
            print("❌ Invalid format. Use csv, json, or html")
            filename = None
        
        if filename:
            print(f"✅ Exported to {filename}")
        else:
            print("❌ Export failed")
    
    elif args.bulk:
        logger.info(f"Bulk analyzing {len(args.bulk)} symbols...")
        results = exporter.bulk_analysis_and_export(args.bulk, 'csv')
        
        successful = sum(1 for r in results.values() if r['status'] == 'success')
        print(f"✅ Successfully analyzed {successful}/{len(args.bulk)} symbols")
        
        for symbol, result in results.items():
            if result['status'] == 'success':
                print(f"  {symbol}: {result['sentiment']['label']} ({result['sentiment']['average_score']:.3f})")
            else:
                print(f"  {symbol}: ❌ {result.get('error', 'Unknown error')}")
    
    elif args.report:
        logger.info(f"Generating report for {args.report}...")
        filename = exporter.generate_html_report(args.report, args.days)
        if filename:
            print(f"✅ Report generated: {filename}")
        else:
            print("❌ Report generation failed")
    
    elif args.stats:
        stats = exporter.get_database_stats()
        print("📊 Database Statistics:")
        print(f"  Total records: {stats.get('total_records', 0)}")
        print(f"  Unique symbols: {stats.get('unique_symbols', 0)}")
        if stats.get('date_range'):
            print(f"  Date range: {stats['date_range']['earliest']} to {stats['date_range']['latest']}")
        print("  Top symbols:")
        for symbol_data in stats.get('top_symbols', []):
            print(f"    {symbol_data['symbol']}: {symbol_data['count']} records")
    
    else:
        parser.print_help()