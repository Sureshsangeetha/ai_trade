#!/usr/bin/env python3
"""
Sentiment-based alert system for monitoring market sentiment changes.
Provides real-time notifications when sentiment crosses thresholds.
"""

import os
import time
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
import logging
from dataclasses import dataclass
from news_sentiment import NewsAndSentimentAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SentimentAlert:
    """Configuration for a sentiment alert"""
    symbol: str
    threshold_positive: float = 0.5
    threshold_negative: float = -0.5
    email: Optional[str] = None
    webhook_url: Optional[str] = None
    check_interval: int = 300  # 5 minutes
    last_checked: Optional[datetime] = None
    last_sentiment: Optional[float] = None
    alert_history: List[Dict] = None
    
    def __post_init__(self):
        if self.alert_history is None:
            self.alert_history = []

class SentimentAlertManager:
    """Manages sentiment-based alerts and notifications"""
    
    def __init__(self, config_file: str = "sentiment_alerts.json"):
        self.config_file = config_file
        self.analyzer = NewsAndSentimentAnalyzer()
        self.alerts: List[SentimentAlert] = []
        self.email_config = {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'email_user': os.getenv('EMAIL_USER', ''),
            'email_password': os.getenv('EMAIL_PASSWORD', ''),
            'from_email': os.getenv('FROM_EMAIL', '')
        }
        self.load_alerts()
    
    def load_alerts(self):
        """Load alerts from configuration file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.alerts = [SentimentAlert(**alert_data) for alert_data in data.get('alerts', [])]
                logger.info(f"Loaded {len(self.alerts)} alerts from {self.config_file}")
            else:
                logger.info(f"No existing alerts file found. Starting with empty alerts.")
        except Exception as e:
            logger.error(f"Error loading alerts: {e}")
    
    def save_alerts(self):
        """Save alerts to configuration file"""
        try:
            data = {
                'alerts': [
                    {
                        'symbol': alert.symbol,
                        'threshold_positive': alert.threshold_positive,
                        'threshold_negative': alert.threshold_negative,
                        'email': alert.email,
                        'webhook_url': alert.webhook_url,
                        'check_interval': alert.check_interval,
                        'last_checked': alert.last_checked.isoformat() if alert.last_checked else None,
                        'last_sentiment': alert.last_sentiment,
                        'alert_history': alert.alert_history
                    }
                    for alert in self.alerts
                ]
            }
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(self.alerts)} alerts to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving alerts: {e}")
    
    def add_alert(self, symbol: str, threshold_positive: float = 0.5, 
                  threshold_negative: float = -0.5, email: str = None,
                  webhook_url: str = None, check_interval: int = 300):
        """Add a new sentiment alert"""
        alert = SentimentAlert(
            symbol=symbol,
            threshold_positive=threshold_positive,
            threshold_negative=threshold_negative,
            email=email,
            webhook_url=webhook_url,
            check_interval=check_interval
        )
        self.alerts.append(alert)
        self.save_alerts()
        logger.info(f"Added alert for {symbol}")
        return alert
    
    def remove_alert(self, symbol: str):
        """Remove an alert by symbol"""
        self.alerts = [alert for alert in self.alerts if alert.symbol != symbol]
        self.save_alerts()
        logger.info(f"Removed alert for {symbol}")
    
    def check_sentiment(self, symbol: str) -> Dict:
        """Check current sentiment for a symbol"""
        try:
            results = self.analyzer.get_comprehensive_sentiment_analysis(symbol)
            if results.get('overall_sentiment'):
                sentiment_score = results['overall_sentiment']['average_score']
                confidence = results['overall_sentiment']['confidence']
                return {
                    'symbol': symbol,
                    'sentiment_score': sentiment_score,
                    'confidence': confidence,
                    'label': results['overall_sentiment']['label'],
                    'sources': results['overall_sentiment']['total_sources'],
                    'timestamp': datetime.now().isoformat()
                }
            return None
        except Exception as e:
            logger.error(f"Error checking sentiment for {symbol}: {e}")
            return None
    
    def should_trigger_alert(self, alert: SentimentAlert, current_sentiment: float) -> bool:
        """Determine if an alert should be triggered"""
        if alert.last_sentiment is None:
            return False
        
        # Check for positive sentiment threshold crossing
        if (alert.last_sentiment <= alert.threshold_positive and 
            current_sentiment > alert.threshold_positive):
            return True
        
        # Check for negative sentiment threshold crossing
        if (alert.last_sentiment >= alert.threshold_negative and 
            current_sentiment < alert.threshold_negative):
            return True
        
        return False
    
    def send_email_alert(self, alert: SentimentAlert, sentiment_data: Dict):
        """Send email notification"""
        if not alert.email or not self.email_config['email_user']:
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from_email'] or self.email_config['email_user']
            msg['To'] = alert.email
            msg['Subject'] = f"📊 Sentiment Alert: {alert.symbol}"
            
            sentiment_emoji = "🟢" if sentiment_data['sentiment_score'] > 0.1 else "🔴" if sentiment_data['sentiment_score'] < -0.1 else "🟡"
            
            body = f"""
            <html>
            <body>
                <h2>{sentiment_emoji} Sentiment Alert: {alert.symbol}</h2>
                <p><strong>Current Sentiment:</strong> {sentiment_data['label']} ({sentiment_data['sentiment_score']:.3f})</p>
                <p><strong>Confidence:</strong> {sentiment_data['confidence']:.1%}</p>
                <p><strong>Sources:</strong> {sentiment_data['sources']} data points</p>
                <p><strong>Timestamp:</strong> {sentiment_data['timestamp']}</p>
                
                <hr>
                <p><strong>Alert Thresholds:</strong></p>
                <ul>
                    <li>Positive: {alert.threshold_positive}</li>
                    <li>Negative: {alert.threshold_negative}</li>
                </ul>
                
                <p><em>This alert was generated by AI Stock Market Analyzer</em></p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['email_user'], self.email_config['email_password'])
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email alert sent for {alert.symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email alert: {e}")
            return False
    
    def send_webhook_alert(self, alert: SentimentAlert, sentiment_data: Dict):
        """Send webhook notification"""
        if not alert.webhook_url:
            return False
        
        try:
            import requests
            
            payload = {
                'symbol': alert.symbol,
                'sentiment_data': sentiment_data,
                'alert_thresholds': {
                    'positive': alert.threshold_positive,
                    'negative': alert.threshold_negative
                },
                'timestamp': datetime.now().isoformat()
            }
            
            response = requests.post(alert.webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Webhook alert sent for {alert.symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending webhook alert: {e}")
            return False
    
    def trigger_alert(self, alert: SentimentAlert, sentiment_data: Dict):
        """Trigger an alert through configured channels"""
        alert_record = {
            'timestamp': datetime.now().isoformat(),
            'sentiment_score': sentiment_data['sentiment_score'],
            'label': sentiment_data['label'],
            'confidence': sentiment_data['confidence']
        }
        
        # Send email if configured
        if alert.email:
            success = self.send_email_alert(alert, sentiment_data)
            alert_record['email_sent'] = success
        
        # Send webhook if configured
        if alert.webhook_url:
            success = self.send_webhook_alert(alert, sentiment_data)
            alert_record['webhook_sent'] = success
        
        # Record alert in history
        alert.alert_history.append(alert_record)
        
        # Keep only last 100 alerts
        if len(alert.alert_history) > 100:
            alert.alert_history = alert.alert_history[-100:]
        
        logger.info(f"Alert triggered for {alert.symbol}: {sentiment_data['label']} ({sentiment_data['sentiment_score']:.3f})")
    
    def check_all_alerts(self):
        """Check all configured alerts"""
        for alert in self.alerts:
            now = datetime.now()
            
            # Check if it's time to check this alert
            if (alert.last_checked and 
                now - alert.last_checked < timedelta(seconds=alert.check_interval)):
                continue
            
            # Get current sentiment
            sentiment_data = self.check_sentiment(alert.symbol)
            if not sentiment_data:
                continue
            
            current_sentiment = sentiment_data['sentiment_score']
            
            # Check if alert should be triggered
            if self.should_trigger_alert(alert, current_sentiment):
                self.trigger_alert(alert, sentiment_data)
            
            # Update alert status
            alert.last_checked = now
            alert.last_sentiment = current_sentiment
        
        self.save_alerts()
    
    def run_monitoring(self, duration_hours: int = 24):
        """Run continuous monitoring for specified duration"""
        end_time = datetime.now() + timedelta(hours=duration_hours)
        logger.info(f"Starting sentiment monitoring for {duration_hours} hours...")
        
        while datetime.now() < end_time:
            try:
                self.check_all_alerts()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)
        
        logger.info("Monitoring completed")
    
    def get_alert_summary(self) -> Dict:
        """Get summary of all alerts"""
        summary = {
            'total_alerts': len(self.alerts),
            'active_alerts': len([a for a in self.alerts if a.last_checked]),
            'alerts_triggered_today': 0,
            'alerts': []
        }
        
        today = datetime.now().date()
        
        for alert in self.alerts:
            alert_info = {
                'symbol': alert.symbol,
                'threshold_positive': alert.threshold_positive,
                'threshold_negative': alert.threshold_negative,
                'last_checked': alert.last_checked.isoformat() if alert.last_checked else None,
                'last_sentiment': alert.last_sentiment,
                'alerts_today': 0
            }
            
            # Count alerts triggered today
            for alert_record in alert.alert_history:
                alert_date = datetime.fromisoformat(alert_record['timestamp']).date()
                if alert_date == today:
                    alert_info['alerts_today'] += 1
                    summary['alerts_triggered_today'] += 1
            
            summary['alerts'].append(alert_info)
        
        return summary

# Example usage and CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Sentiment Alert Manager")
    parser.add_argument('--add', nargs=2, metavar=('SYMBOL', 'EMAIL'), 
                       help='Add new alert for symbol with email')
    parser.add_argument('--remove', metavar='SYMBOL', help='Remove alert for symbol')
    parser.add_argument('--list', action='store_true', help='List all alerts')
    parser.add_argument('--check', metavar='SYMBOL', help='Check sentiment for symbol')
    parser.add_argument('--monitor', type=int, metavar='HOURS', 
                       help='Run monitoring for specified hours')
    parser.add_argument('--summary', action='store_true', help='Show alert summary')
    
    args = parser.parse_args()
    
    manager = SentimentAlertManager()
    
    if args.add:
        symbol, email = args.add
        manager.add_alert(symbol, email=email)
        print(f"✅ Added alert for {symbol}")
    
    elif args.remove:
        manager.remove_alert(args.remove)
        print(f"✅ Removed alert for {args.remove}")
    
    elif args.list:
        print("📋 Current Alerts:")
        for alert in manager.alerts:
            print(f"  {alert.symbol}: +{alert.threshold_positive}, -{alert.threshold_negative}")
    
    elif args.check:
        sentiment_data = manager.check_sentiment(args.check)
        if sentiment_data:
            print(f"📊 {args.check}: {sentiment_data['label']} ({sentiment_data['sentiment_score']:.3f})")
        else:
            print(f"❌ Could not get sentiment for {args.check}")
    
    elif args.monitor:
        manager.run_monitoring(args.monitor)
    
    elif args.summary:
        summary = manager.get_alert_summary()
        print(f"📊 Alert Summary:")
        print(f"  Total alerts: {summary['total_alerts']}")
        print(f"  Active alerts: {summary['active_alerts']}")
        print(f"  Alerts triggered today: {summary['alerts_triggered_today']}")
    
    else:
        parser.print_help()