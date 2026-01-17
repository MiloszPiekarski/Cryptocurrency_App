"""
CASH MAELSTROM - DataIngestor (Layer 1: The Veins)
Fetches real-time market data from exchanges and writes to Cloud SQL (Hot Storage).
"""

import asyncio
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
import ccxt.async_support as ccxt_async
import ccxt as ccxt_sync # Synchronous for backfill
import psycopg2
from psycopg2.extras import execute_batch
from loguru import logger
import redis

from cloud_config import (
    CLOUD_SQL_IP, CLOUD_SQL_DATABASE, CLOUD_SQL_USER, CLOUD_SQL_PASSWORD,
    SUPPORTED_SYMBOLS, EXCHANGE_ID
)

# SHIFT YEARS CONSTANT FOR BACKFILL
SHIFT_YEARS = 1

class DataIngestor:
    """
    Layer 1: The Veins
    
    Ingests real-time market data from exchanges and routes it to:
    1. Cloud SQL (Hot Storage) - for dashboard queries
    2. Redis (Cache) - for instant WebSocket delivery
    3. Self-Healing Backfill - ensures continuity on restart.
    """
    
    def __init__(self, symbols: List[str] = None):
        self.symbols = symbols or SUPPORTED_SYMBOLS
        self.exchange = None
        self.db_conn = None
        self.redis_client = None
        self.running = False
        
    def connect_cloud_sql(self):
        """Connect to Google Cloud SQL (Hot Storage)"""
        logger.info("🔌 Connecting to Cloud SQL (maelstrom-db)...")
        try:
            self.db_conn = psycopg2.connect(
                host=CLOUD_SQL_IP,
                port=5432,
                dbname=CLOUD_SQL_DATABASE,
                user=CLOUD_SQL_USER,
                password=CLOUD_SQL_PASSWORD
            )
            self.db_conn.autocommit = False
            logger.success("✅ Connected to Cloud SQL!")
        except Exception as e:
            logger.error(f"❌ Cloud SQL Connection Failed: {e}")
            raise
        
    def connect_redis(self):
        """Connect to Redis for real-time cache"""
        try:
            self.redis_client = redis.from_url('redis://localhost:6379', decode_responses=True)
            self.redis_client.ping()
            logger.success("✅ Connected to Redis!")
        except Exception as e:
            logger.warning(f"Redis not available: {e}")
            self.redis_client = None
    
    async def connect_exchange(self):
        """Connect to exchange via CCXT"""
        exchange_class = getattr(ccxt_async, EXCHANGE_ID)
        self.exchange = exchange_class({'enableRateLimit': True})
        logger.success(f"✅ Connected to {EXCHANGE_ID.upper()}!")
        
    def self_healing_backfill(self):
        """
        Runs on startup.
        Checks the last recorded timestamp in Cloud SQL for each symbol.
        If there's a gap > 1 hour, fetches missing data from CCXT (Bitstamp/Binance).
        """
        logger.info("🚑 STARTING SELF-HEALING BACKFILL...")
        
        # Use synchronous CCXT for this blocking operation (simpler safety)
        exchange = ccxt_sync.binance() 
        
        if not self.db_conn:
            self.connect_cloud_sql()
            
        cursor = self.db_conn.cursor()
        
        for symbol in self.symbols:
            try:
                # 1. GAP DETECTION (Smart Scan)
                # Instead of just MAX(time), we look for the OLDEST missing hour in the last 24h.
                cursor.execute("SELECT MAX(time) FROM ohlcv WHERE symbol = %s", (symbol,))
                result = cursor.fetchone()
                last_time_db = result[0] if result else None

                now = datetime.now(timezone.utc)
                lookback_hours = 24
                scan_start = now - timedelta(hours=lookback_hours)
                
                # Default: If no data, start from 48h ago
                start_ts = int((now - timedelta(hours=48)).timestamp() * 1000)
                
                if last_time_db:
                    # Get all existing timestamps in the window
                    cursor.execute("""
                        SELECT time FROM ohlcv 
                        WHERE symbol = %s AND time >= %s
                        ORDER BY time ASC
                    """, (symbol, scan_start))
                    rows = cursor.fetchall()
                    existing_times = {r[0].replace(tzinfo=timezone.utc) for r in rows}
                    
                    found_gap = False
                    check_time = scan_start.replace(minute=0, second=0, microsecond=0)
                    
                    while check_time < now - timedelta(minutes=5): # Buffer for current forming candle
                        if check_time not in existing_times:
                            logger.warning(f"⚠️ GAP FOUND for {symbol} at {check_time}. Rewinding fetcher...")
                            start_ts = int(check_time.timestamp() * 1000)
                            found_gap = True
                            break
                        check_time += timedelta(hours=1)
                        
                    if not found_gap:
                        # Fallback to MAX(time) check if no holes found
                        last_time_db = last_time_db.replace(tzinfo=timezone.utc)
                        if (now - last_time_db) > timedelta(minutes=65):
                             start_ts = int(last_time_db.timestamp() * 1000)
                        else:
                             logger.info(f"✅ {symbol} is fully synchronized.")
                             continue
                else:
                    logger.warning(f"⚠️ No data for {symbol}. Initializing full backfill...")

                # 2. Fetch from Exchange
                # NATIVE MODE: Fetch directly (Exchange has 2026 data)
                request_ts = start_ts 
                
                ohlcv = exchange.fetch_ohlcv(symbol, '1h', since=request_ts, limit=100)
                
                if not ohlcv:
                    continue
                    
                # 3. Insert Loop
                count = 0
                for candle in ohlcv:
                    ts, open_, high, low, close, vol = candle
                    
                    # NATIVE MODE: No shift
                    c_dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
                            
                    cursor.execute("""
                        INSERT INTO ohlcv (time, symbol, timeframe, open, high, low, close, volume)
                        VALUES (%s, %s, '1h', %s, %s, %s, %s, %s)
                        ON CONFLICT (time, symbol, timeframe) DO UPDATE SET close = EXCLUDED.close
                    """, (c_dt, symbol, open_, high, low, close, vol))
                    count += 1
                    
                self.db_conn.commit()
                logger.success(f"🩹 Healed {count} candles for {symbol}")
                
            except Exception as e:
                logger.error(f"Failed to heal {symbol}: {e}")
                self.db_conn.rollback()

        cursor.close()
        logger.info("🏁 SELF-HEALING COMPLETE.")

    async def fetch_ticker(self, symbol: str) -> Optional[Dict]:
        """Fetch current ticker from exchange"""
        try:
            ticker = await self.exchange.fetch_ticker(symbol)
            
            # NATIVE MODE: No shift
            ts = ticker['timestamp']
            dt = datetime.fromtimestamp(ts/1000, tz=timezone.utc)
            
            return {
                'symbol': symbol,
                'price': ticker['last'],
                'volume': ticker['quoteVolume'] or 0,
                'bid': ticker.get('bid'),
                'ask': ticker.get('ask'),
                'high': ticker.get('high'),
                'low': ticker.get('low'),
                'change_24h': ticker.get('percentage', 0),
                'timestamp': ts,
                'datetime': dt.isoformat()
            }
        except Exception as e:
            logger.warning(f"Ticker fetch failed for {symbol}: {e}")
            return None
    
    async def fetch_order_book(self, symbol: str, limit: int = 20) -> Optional[Dict]:
        """Fetch order book depth from exchange"""
        try:
            orderbook = await self.exchange.fetch_order_book(symbol, limit)
            return {
                'symbol': symbol,
                'bids': orderbook['bids'][:limit],
                'asks': orderbook['asks'][:limit],
                'timestamp': orderbook.get('timestamp') or int(datetime.now().timestamp() * 1000)
            }
        except Exception as e:
            logger.warning(f"Order book fetch failed for {symbol}: {e}")
            return None
    
    def save_orderbook_to_redis(self, data: Dict):
        """Store order book in Redis for API access"""
        if not self.redis_client or not data:
            return
            
        try:
            symbol_key = data['symbol'].replace('/', '')
            self.redis_client.setex(
                f"orderbook:{symbol_key}",
                60,  # 1 minute TTL
                json.dumps(data)
            )
        except Exception as e:
            logger.warning(f"OrderBook Redis save failed: {e}")
            
    def save_to_cloud_sql(self, data: Dict):
        """
        Write tick data to Cloud SQL (Hot Storage).
        This is the PRIMARY data destination.
        """
        if not data or not self.db_conn:
            return
            
        try:
            cursor = self.db_conn.cursor()
            
            # Insert into market_history
            cursor.execute("""
                INSERT INTO market_history (time, symbol, price, volume, source)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                datetime.fromtimestamp(data['timestamp'] / 1000.0, tz=timezone.utc),
                data['symbol'],
                data['price'],
                data['volume'],
                'binance'
            ))
            
            self.db_conn.commit()
            cursor.close()
            
        except Exception as e:
            logger.error(f"Cloud SQL write failed: {e}")
            self.db_conn.rollback()
            
    def publish_to_redis(self, data: Dict):
        """
        Publish to Redis for real-time dashboard updates.
        This enables the "WOW effect" - prices blinking in real-time.
        """
        if not self.redis_client or not data:
            return
            
        try:
            symbol_key = data['symbol'].replace('/', '')
            
            # Store in cache (for API reads)
            redis_data = {
                'symbol': data['symbol'],
                'last': data['price'],
                'bid': data.get('bid'),
                'ask': data.get('ask'),
                'high': data.get('high'),
                'low': data.get('low'),
                'volume': data['volume'],
                'change_24h': data.get('change_24h', 0),
                'timestamp': data['timestamp'],
                'datetime': data['datetime']
            }
            
            self.redis_client.setex(
                f"ticker:{symbol_key}",
                120,
                json.dumps(redis_data)
            )
            
            # Publish for WebSocket subscribers
            self.redis_client.publish('market:tickers', json.dumps(redis_data))
            
        except Exception as e:
            logger.warning(f"Redis publish failed: {e}")
    
    async def ingest_symbol(self, symbol: str):
        """Ingest all data for a single symbol"""
        # 1. Fetch ticker
        data = await self.fetch_ticker(symbol)
        if data:
            # Save to Cloud SQL (Hot Storage)
            self.save_to_cloud_sql(data)
            # Publish to Redis (Real-time)
            self.publish_to_redis(data)
            logger.debug(f"📈 {symbol}: ${data['price']:,.2f}")
        
        # 2. Fetch order book (every 5th cycle to reduce load)
        orderbook = await self.fetch_order_book(symbol, limit=20)
        if orderbook:
            self.save_orderbook_to_redis(orderbook)
            
    async def run(self, poll_interval: float = 1.0):
        """
        Main ingestion loop.
        Continuously polls all symbols and writes to Hot Storage.
        """
        logger.info("="*60)
        logger.info("CASH MAELSTROM - DataIngestor (The Veins)")
        logger.info("="*60)
        
        # Initialize connections
        self.connect_cloud_sql()
        self.connect_redis()
        
        # --- SELF HEALING ON STARTUP ---
        self.self_healing_backfill()
        # -------------------------------
        
        await self.connect_exchange()
        
        logger.info(f"📊 Tracking {len(self.symbols)} symbols")
        logger.info(f"⏱️ Poll interval: {poll_interval}s")
        logger.info("-"*60)
        
        self.running = True
        cycle = 0
        
        while self.running:
            cycle += 1
            tasks = [self.ingest_symbol(s) for s in self.symbols]
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
            if cycle % 10 == 0:
                logger.info(f"📊 Cycle {cycle}: {len(self.symbols)} symbols ingested")
                
            await asyncio.sleep(poll_interval)
            
    async def shutdown(self):
        """Clean shutdown"""
        self.running = False
        if self.exchange:
            await self.exchange.close()
        if self.db_conn:
            self.db_conn.close()
        logger.info("🛑 DataIngestor stopped")


if __name__ == "__main__":
    ingestor = DataIngestor()
    
    try:
        asyncio.run(ingestor.run(poll_interval=20.0)) # Relaxed poll interval for REST
    except KeyboardInterrupt:
        logger.info("Stopped by user")
