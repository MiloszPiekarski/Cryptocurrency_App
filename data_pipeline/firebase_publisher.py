"""
CASH MAELSTROM - Firebase Realtime Publisher
Pushes live price updates to Firebase Realtime Database for instant frontend updates.

This creates the "WOW Effect" - prices blinking in real-time without page refresh.
Flow: Exchange → Ingestor → Firebase Realtime DB → React (via onValue listener)
"""

import firebase_admin
from firebase_admin import credentials, db
import json
from datetime import datetime
from typing import Dict, Optional
from loguru import logger
import redis
import time
import threading


class FirebaseRealtimePublisher:
    """
    Publishes live price data to Firebase Realtime Database.
    
    Frontend subscribes to:
    - /prices/{symbol} - for individual symbol updates
    - /tickers - for all symbols
    
    React component uses onValue() listener for real-time updates.
    """
    
    def __init__(self, credentials_path: str = None):
        self.initialized = False
        self.db_ref = None
        self.redis_client = None
        
        # Firebase configuration
        self.firebase_url = "https://cash-maelstrom-default-rtdb.europe-west1.firebasedatabase.app"
        
    def initialize(self, credentials_path: str = None):
        """Initialize Firebase Admin SDK using ADC or Service Account"""
        try:
            if not firebase_admin._apps:
                if credentials_path:
                    # Legacy method: Use explicit key file
                    cred = credentials.Certificate(credentials_path)
                    firebase_admin.initialize_app(cred, {
                        'databaseURL': self.firebase_url
                    })
                else:
                    # Cloud Native method: Use Application Default Credentials (ADC)
                    # Works automatically on Cloud Run, Cloud Functions, and authorized local CLI
                    cred = credentials.ApplicationDefault()
                    firebase_admin.initialize_app(cred, {
                        'databaseURL': self.firebase_url
                    })
                    
            self.db_ref = db.reference()
            self.initialized = True
            logger.success("✅ Firebase connected via Google ADC!")
            
        except Exception as e:
            logger.warning(f"Firebase init failed: {e}")
            logger.info("ℹ️  Tip: Run 'gcloud auth application-default login' to fix local access")
            self.initialized = False
    
    def connect_redis(self):
        """Connect to Redis to listen for price updates"""
        try:
            self.redis_client = redis.from_url('redis://localhost:6379', decode_responses=True)
            self.redis_client.ping()
            logger.success("✅ Redis connected for Firebase bridge!")
        except Exception as e:
            logger.warning(f"Redis unavailable: {e}")
            
    def publish_price(self, symbol: str, data: Dict):
        """
        Publish single price update to Firebase.
        Path: /prices/{BTCUSDT}
        """
        if not self.initialized:
            return
            
        try:
            symbol_key = symbol.replace('/', '')
            
            price_data = {
                'symbol': symbol,
                'price': data.get('last', data.get('price', 0)),
                'change24h': data.get('change_24h', 0),
                'volume': data.get('volume', 0),
                'timestamp': data.get('timestamp', int(datetime.now().timestamp() * 1000)),
                'updated': datetime.now().isoformat()
            }
            
            # Update Firebase
            self.db_ref.child('prices').child(symbol_key).set(price_data)
            
        except Exception as e:
            logger.debug(f"Firebase publish error: {e}")
    
    def publish_all_tickers(self, tickers: Dict):
        """
        Publish all tickers at once.
        Path: /tickers
        """
        if not self.initialized:
            return
            
        try:
            self.db_ref.child('tickers').set(tickers)
        except Exception as e:
            logger.debug(f"Firebase bulk publish error: {e}")
    
    def publish_orderbook(self, symbol: str, orderbook: Dict):
        """
        Publish order book to Firebase.
        Path: /orderbooks/{BTCUSDT}
        """
        if not self.initialized:
            return
            
        try:
            symbol_key = symbol.replace('/', '')
            self.db_ref.child('orderbooks').child(symbol_key).set({
                'bids': orderbook.get('bids', [])[:10],
                'asks': orderbook.get('asks', [])[:10],
                'timestamp': int(datetime.now().timestamp() * 1000)
            })
        except Exception as e:
            logger.debug(f"Firebase orderbook error: {e}")
    
    def listen_redis_and_publish(self):
        """
        Bridge: Listen to Redis pub/sub and forward to Firebase.
        This connects the WebSocket Ingestor to Firebase.
        """
        if not self.redis_client:
            self.connect_redis()
            
        if not self.redis_client:
            logger.error("Cannot start Firebase bridge without Redis")
            return
            
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe('market:tickers')
        
        logger.info("🔥 Firebase bridge listening to Redis...")
        
        for message in pubsub.listen():
            if message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    self.publish_price(data.get('symbol', ''), data)
                except:
                    pass
    
    def run_bridge(self):
        """Run the Redis→Firebase bridge in a background thread"""
        thread = threading.Thread(target=self.listen_redis_and_publish, daemon=True)
        thread.start()
        logger.info("🔥 Firebase Realtime bridge started!")
        return thread


# Singleton instance
firebase_publisher = FirebaseRealtimePublisher()


def start_firebase_bridge(credentials_path: str = None):
    """Start the Firebase bridge (call on app startup)"""
    firebase_publisher.initialize(credentials_path)
    firebase_publisher.run_bridge()


if __name__ == "__main__":
    # Test run
    logger.info("Starting Firebase Realtime Publisher...")
    firebase_publisher.initialize()
    firebase_publisher.connect_redis()
    firebase_publisher.listen_redis_and_publish()
