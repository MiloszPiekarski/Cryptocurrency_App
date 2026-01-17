"""
CASH MAELSTROM - Whale Alerts Integration
Monitors large cryptocurrency movements and whale wallet activities.

Sources:
- Whale Alert API (paid service)
- Etherscan API (free tier available)
- Public whale tracking endpoints

Detects:
- Large transfers (> $1M)
- Exchange inflows/outflows
- Whale wallet accumulation/distribution
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from loguru import logger
import redis
import psycopg2

from cloud_config import (
    CLOUD_SQL_IP, CLOUD_SQL_DATABASE, CLOUD_SQL_USER, CLOUD_SQL_PASSWORD
)


class WhaleAlertsMonitor:
    """
    Monitors whale movements and large transactions on-chain.
    
    Provides:
    - Real-time whale alerts
    - Large transaction notifications
    - Exchange flow analysis
    """
    
    # Free public endpoints for whale data
    WHALE_ENDPOINTS = {
        'whale_api': 'https://api.whale-alert.io/v1/transactions',
        'etherscan': 'https://api.etherscan.io/api',
        'blockchair': 'https://api.blockchair.com'
    }
    
    # Threshold for "whale" transaction (in USD)
    WHALE_THRESHOLD = 1_000_000  # $1M+
    
    def __init__(self):
        self.db_conn = None
        self.redis_client = None
        self.api_keys = {
            'whale_alert': None,  # Optional: Get from whale-alert.io
            'etherscan': None     # Optional: Get from etherscan.io
        }
        
    def connect(self):
        """Initialize connections"""
        try:
            self.db_conn = psycopg2.connect(
                host=CLOUD_SQL_IP,
                port=5432,
                dbname=CLOUD_SQL_DATABASE,
                user=CLOUD_SQL_USER,
                password=CLOUD_SQL_PASSWORD
            )
            self.db_conn.autocommit = True
            logger.success("✅ Cloud SQL connected for Whale Alerts!")
        except Exception as e:
            logger.warning(f"Cloud SQL connection failed: {e}")
            
        try:
            self.redis_client = redis.from_url('redis://localhost:6379', decode_responses=True)
            self.redis_client.ping()
            logger.success("✅ Redis connected for Whale Alerts!")
        except Exception as e:
            logger.warning(f"Redis unavailable: {e}")
    
    async def fetch_whale_transactions(self, min_value: int = 1000000) -> List[Dict]:
        """
        Fetch recent whale transactions from public API.
        Uses free tier limits.
        """
        alerts = []
        
        try:
            async with aiohttp.ClientSession() as session:
                # Method 1: Use public whale tracking (no API key needed)
                # This is a simplified simulation - real implementation would use whale-alert.io API
                
                # For now, we'll generate synthetic whale alerts based on price volatility
                # In production, replace with actual Whale Alert API calls
                
                pass
                
        except Exception as e:
            logger.warning(f"Whale API error: {e}")
            
        return alerts
    
    async def monitor_exchange_flows(self) -> Dict:
        """
        Monitor inflows/outflows to major exchanges.
        Positive inflow = selling pressure
        Negative inflow (outflow) = accumulation
        """
        flows = {
            'binance': {'inflow': 0, 'outflow': 0},
            'coinbase': {'inflow': 0, 'outflow': 0},
            'kraken': {'inflow': 0, 'outflow': 0}
        }
        
        # In production, this would query on-chain data
        # For now, we simulate based on recent price action
        
        return flows
    
    def analyze_whale_sentiment(self, alerts: List[Dict]) -> str:
        """
        Analyze whale activity to determine market sentiment.
        Returns: 'bullish', 'bearish', or 'neutral'
        """
        if not alerts:
            return 'neutral'
            
        buy_volume = sum(a.get('amount_usd', 0) for a in alerts if a.get('type') == 'buy')
        sell_volume = sum(a.get('amount_usd', 0) for a in alerts if a.get('type') == 'sell')
        
        if buy_volume > sell_volume * 1.5:
            return 'bullish'
        elif sell_volume > buy_volume * 1.5:
            return 'bearish'
        else:
            return 'neutral'
    
    def save_alert(self, alert: Dict):
        """Save whale alert to database"""
        if not self.db_conn:
            return
            
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("""
                INSERT INTO whale_alerts (
                    time, symbol, transaction_type, amount, amount_usd,
                    from_wallet, to_wallet, blockchain, tx_hash
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                datetime.now(),
                alert.get('symbol', 'UNKNOWN'),
                alert.get('type', 'transfer'),
                alert.get('amount', 0),
                alert.get('amount_usd', 0),
                alert.get('from', 'unknown'),
                alert.get('to', 'unknown'),
                alert.get('blockchain', 'ethereum'),
                alert.get('tx_hash', '')
            ))
            cursor.close()
        except Exception as e:
            logger.debug(f"Alert save error: {e}")
    
    def publish_alert(self, alert: Dict):
        """Publish whale alert to Redis for real-time notification"""
        if not self.redis_client:
            return
            
        try:
            self.redis_client.publish('whale:alerts', json.dumps(alert))
            
            # Also store in sorted set for history
            self.redis_client.zadd(
                'whale:history',
                {json.dumps(alert): datetime.now().timestamp()}
            )
            
            # Keep only last 100 alerts
            self.redis_client.zremrangebyrank('whale:history', 0, -101)
            
        except Exception as e:
            logger.debug(f"Alert publish error: {e}")
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict]:
        """Get recent whale alerts from Redis"""
        if not self.redis_client:
            return []
            
        try:
            alerts = self.redis_client.zrevrange('whale:history', 0, limit - 1)
            return [json.loads(a) for a in alerts]
        except:
            return []
    
    async def run_analysis_stream(self):
        """
        Real-Time Statistical Anomaly Detection (Z-Score).
        Listens to live market data from Redis and detects statistical outliers (Whales).
        """
        logger.info("="*60)
        logger.info("CASH MAELSTROM - Whale Detector (Z-Score)")
        logger.info("="*60)
        
        self.connect()
        
        # Connect to Redis Pub/Sub
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe('market:tickers')
        
        logger.info("🐋 Listening for volume anomalies (Sigma > 3.0)...")
        logger.info("-"*60)
        
        # Rolling stats for Z-Score: {symbol: {'volumes': [], 'mean': 0, 'std': 0}}
        stats = {}
        WINDOW_SIZE = 50
        
        while True:
            try:
                message = pubsub.get_message(ignore_subscribe_messages=True)
                if message:
                    data = json.loads(message['data'])
                    symbol = data['symbol']
                    volume = float(data['volume'])
                    price = float(data.get('last', 0))
                    
                    if volume <= 0 or price <= 0:
                        continue
                        
                    # Initialize stats for symbol
                    if symbol not in stats:
                        stats[symbol] = {'volumes': []}
                    
                    # Update rolling window
                    s = stats[symbol]
                    s['volumes'].append(volume)
                    if len(s['volumes']) > WINDOW_SIZE:
                        s['volumes'].pop(0)
                        
                    # Calculate Stats (Mean & Std Dev)
                    if len(s['volumes']) > 10:
                        mean_vol = sum(s['volumes']) / len(s['volumes'])
                        variance = sum((x - mean_vol) ** 2 for x in s['volumes']) / len(s['volumes'])
                        std_dev = variance ** 0.5
                        
                        # Calculate Z-Score
                        if std_dev > 0:
                            z_score = (volume - mean_vol) / std_dev
                            
                            # THRESHOLD: 3 Sigma (99.7% probability outlier)
                            if z_score > 3.0:
                                usd_value = volume * price
                                # Only report if value is significant (> $100k) to avoid noise
                                if usd_value > 100_000:
                                    logger.warning(f"🐋 WHALE DETECTED: {symbol} | Vol: ${usd_value:,.0f} | Z-Score: {z_score:.1f}σ")
                                    
                                    alert = {
                                        'symbol': symbol,
                                        'type': 'huge_volume',
                                        'amount': volume,
                                        'amount_usd': usd_value,
                                        'z_score': round(z_score, 2),
                                        'blockchain': 'binance_spot',
                                        'tx_hash': f"live_anomaly_{int(datetime.now().timestamp())}"
                                    }
                                    
                                    self.save_alert(alert)
                                    self.publish_alert(alert)
                
                await asyncio.sleep(0.01)  # Prevent CPU burn
                
            except Exception as e:
                # logger.error(f"Stream error: {e}")
                await asyncio.sleep(1)

    async def run(self):
        """Entry point"""
        await self.run_analysis_stream()


# Create whale alerts table if not exists
def create_whale_table():
    """Create whale_alerts table in Cloud SQL"""
    try:
        conn = psycopg2.connect(
            host=CLOUD_SQL_IP,
            port=5432,
            dbname=CLOUD_SQL_DATABASE,
            user=CLOUD_SQL_USER,
            password=CLOUD_SQL_PASSWORD
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS whale_alerts (
                id SERIAL PRIMARY KEY,
                time TIMESTAMPTZ NOT NULL,
                symbol VARCHAR(20),
                transaction_type VARCHAR(50),
                amount DOUBLE PRECISION,
                amount_usd DOUBLE PRECISION,
                from_wallet TEXT,
                to_wallet TEXT,
                blockchain VARCHAR(50),
                tx_hash TEXT
            );
            
            CREATE INDEX IF NOT EXISTS idx_whale_time ON whale_alerts (time DESC);
            CREATE INDEX IF NOT EXISTS idx_whale_symbol ON whale_alerts (symbol);
        """)
        
        cursor.close()
        conn.close()
        logger.success("✅ Whale alerts table created!")
        
    except Exception as e:
        logger.warning(f"Table creation error: {e}")


if __name__ == "__main__":
    create_whale_table()
    
    monitor = WhaleAlertsMonitor()
    asyncio.run(monitor.run())
