"""
CASH MAELSTROM - WebSocket DataIngestor (The Veins - Real-time Edition)
Uses WebSocket streams for millisecond-level data updates.

This replaces REST polling with persistent WebSocket connections for:
- Real-time price ticks
- Order book updates
- Trade streams
"""

import asyncio
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
import websockets
import psycopg2
import redis
from loguru import logger

from cloud_config import (
    CLOUD_SQL_IP, CLOUD_SQL_DATABASE, CLOUD_SQL_USER, CLOUD_SQL_PASSWORD,
    SUPPORTED_SYMBOLS
)


class WebSocketIngestor:
    """
    Layer 1: The Veins (WebSocket Edition)
    
    Maintains persistent WebSocket connections to exchanges for:
    - Ticker updates (every trade)
    - Order book depth updates
    - Aggregated trade streams
    """
    
    # Binance WebSocket endpoints
    BINANCE_WS_BASE = "wss://stream.binance.com:9443/ws"
    BINANCE_WS_STREAM = "wss://stream.binance.com:9443/stream?streams="
    
    def __init__(self, symbols: List[str] = None):
        self.symbols = symbols or SUPPORTED_SYMBOLS[:20]  # Limit for stability
        self.db_conn = None
        self.redis_client = None
        self.running = False
        self.reconnect_delay = 5
        
    def connect_cloud_sql(self):
        """Connect to Google Cloud SQL"""
        logger.info("🔌 Connecting to Cloud SQL...")
        self.db_conn = psycopg2.connect(
            host=CLOUD_SQL_IP,
            port=5432,
            dbname=CLOUD_SQL_DATABASE,
            user=CLOUD_SQL_USER,
            password=CLOUD_SQL_PASSWORD
        )
        self.db_conn.autocommit = True
        logger.success("✅ Cloud SQL connected!")
        
    def connect_redis(self):
        """Connect to Redis for real-time cache"""
        try:
            self.redis_client = redis.from_url('redis://localhost:6379', decode_responses=True)
            self.redis_client.ping()
            logger.success("✅ Redis connected!")
        except Exception as e:
            logger.warning(f"Redis unavailable: {e}")
            self.redis_client = None
    
    def _build_stream_url(self) -> str:
        """Build combined stream URL for all symbols"""
        streams = []
        for symbol in self.symbols:
            symbol_lower = symbol.replace('/', '').lower()
            streams.append(f"{symbol_lower}@ticker")      # Price ticker
            streams.append(f"{symbol_lower}@depth10")     # Order book top 10
        
        return self.BINANCE_WS_STREAM + "/".join(streams)
    
    def _process_ticker(self, data: Dict):
        """Process ticker update from WebSocket"""
        try:
            symbol_raw = data['s']  # e.g., "BTCUSDT"
            symbol = f"{symbol_raw[:-4]}/{symbol_raw[-4:]}"  # "BTC/USDT"
            
            
            # TIME TRAVEL CORRECTION - DISABLED (Exchange is already 2026 aligned)
            final_timestamp = data['E']
            
            # Price Calibration REMOVED (OKX/Binance aligned)
            
            ticker_data = {
                'symbol': symbol,
                'last': float(data['c']),  # Close price
                'bid': float(data['b']),
                'ask': float(data['a']),
                'high': float(data['h']),
                'low': float(data['l']),
                'volume': float(data['q']),  # Quote volume
                'change_24h': float(data['P']),  # Price change percent
                'timestamp': final_timestamp,  # ADJUSTED Time
                'datetime': datetime.fromtimestamp(final_timestamp / 1000, tz=timezone.utc).isoformat()
            }
            
            # Save to Cloud SQL
            self._save_tick(ticker_data)
            
            # Publish to Redis
            self._publish_redis(ticker_data)
            
        except Exception as e:
            logger.debug(f"Ticker processing error: {e}")
    
    def _process_depth(self, data: Dict, stream_name: str = None):
        """Process order book update from WebSocket"""
        try:
            # Extract symbol from stream name or data
            symbol_raw = data.get('s', '')
            if not symbol_raw and stream_name:
                # Extract from stream name e.g., "btcusdt@depth10"
                symbol_raw = stream_name.split('@')[0].upper()
            
            if not symbol_raw:
                return
                
            symbol = f"{symbol_raw[:-4]}/{symbol_raw[-4:]}"
            
            orderbook = {
                'symbol': symbol,
                'bids': [[float(b[0]), float(b[1])] for b in data.get('bids', [])],
                'asks': [[float(a[0]), float(a[1])] for a in data.get('asks', [])],
                'timestamp': int(datetime.now(timezone.utc).timestamp() * 1000)
            }
            
            # Save to Redis only (order book is ephemeral)
            if self.redis_client:
                key = f"orderbook:{symbol.replace('/', '')}"
                self.redis_client.setex(key, 60, json.dumps(orderbook))
                
        except Exception as e:
            logger.debug(f"Depth processing error: {e}")
    
    def _save_tick(self, data: Dict):
        """Save tick to Cloud SQL and update current Candles for ALL timeframes"""
        if not self.db_conn:
            return
            
        try:
            cursor = self.db_conn.cursor()
            
            # 1. Insert Tick (History)
            # Input 'data' already has adjusted timestamp (from _process_ticker)
            
            cursor.execute("""
                INSERT INTO market_history (time, symbol, price, volume, source)
                VALUES (%s, %s, %s, %s, 'websocket')
            """, (
                datetime.fromtimestamp(data['timestamp'] / 1000.0, tz=timezone.utc),
                data['symbol'],
                data['last'],
                data['volume']
            ))
            
            # 2. Update Real-Time Candles for ALL Timeframes
            # This ensures 30m, 1h, etc. charts are also live
            ts = data['timestamp'] / 1000.0
            price = data['last']
            volume = data['volume']  # Note: Volume aggregation is approximate here
            
            timeframes = {
                '1m': 60,
                '5m': 300,
                '15m': 900,
                '30m': 1800,
                '1h': 3600,
                '4h': 14400,
                '1d': 86400
            }

            # Gap Check & repair
            # For each timeframe, check if we missed the previous candle close
            # If so, fill it with the previous known price to maintain continuity.
            for tf_name, tf_seconds in timeframes.items():
                current_candle_ts = ts - (ts % tf_seconds)
                # Look back: check if 'current_candle_ts - tf_seconds' exists
                # OPTIMIZATION: In high-frequency loop, we can't query DB every time.
                # Ideally, this should be handled by a separate validatior or using Redis cache for 'last_seen_candle'.
                # For now, we assume implicit continuity via UPSERT, but if we wanted "Fill Gap", we would do it here.
                # However, filling gaps with 'current price' is dangerous (interpolation). 
                # Better approach: Just ensure the CURRENT candle is updated.
                pass 

            
            for tf_name, tf_seconds in timeframes.items():
                # Calculate start of the candle for this timeframe
                candle_ts = ts - (ts % tf_seconds)
                candle_time = datetime.fromtimestamp(candle_ts, tz=timezone.utc)
                
                # UPSERT logic
                cursor.execute("""
                    INSERT INTO ohlcv (time, symbol, timeframe, open, high, low, close, volume)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 0)
                    ON CONFLICT (time, symbol, timeframe) DO UPDATE SET
                        high = GREATEST(ohlcv.high, EXCLUDED.high),
                        low = LEAST(ohlcv.low, EXCLUDED.low),
                        close = EXCLUDED.close,
                        volume = ohlcv.volume + EXCLUDED.volume;
                """, (
                    candle_time,
                    data['symbol'],
                    tf_name,
                    price, # open (if new)
                    price, # high
                    price, # low
                    price  # close
                ))
            
            self.db_conn.commit()  # EXPLICT COMMIT IS CRITICAL
            # logger.info(f"Saved tick & candles for {data['symbol']} at {candle_time}")
            
            cursor.close()
        except Exception as e:
            self.db_conn.rollback()
            logger.debug(f"DB save error: {e}")
    
    def _publish_redis(self, data: Dict):
        """Publish to Redis for real-time dashboard"""
        if not self.redis_client:
            return
            
        try:
            symbol_key = data['symbol'].replace('/', '')
            
            # Store in cache
            self.redis_client.setex(
                f"ticker:{symbol_key}",
                120,
                json.dumps(data)
            )
            
            # Publish for WebSocket subscribers (Global)
            self.redis_client.publish('market:tickers', json.dumps(data))
            
            # Publish to Symbol Specific Channel (for Frontend)
            self.redis_client.publish(f"ticker:{symbol_key}", json.dumps(data))
            
        except Exception as e:
            logger.debug(f"Redis publish error: {e}")
    
    async def _handle_message(self, message: str):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            
            # Combined stream format
            if 'stream' in data:
                stream = data['stream']
                payload = data['data']
                
                if '@ticker' in stream:
                    self._process_ticker(payload)
                elif '@depth' in stream:
                    self._process_depth(payload, stream)
                    
            # Single stream format
            elif 'e' in data:
                if data['e'] == '24hrTicker':
                    self._process_ticker(data)
                elif data['e'] == 'depthUpdate':
                    self._process_depth(data)
                    
        except json.JSONDecodeError:
            pass
        except Exception as e:
            logger.debug(f"Message handling error: {e}")
    
    async def run(self):
        """Main WebSocket loop with auto-reconnect"""
        logger.info("="*60)
        logger.info("CASH MAELSTROM - WebSocket Ingestor (The Veins)")
        logger.info("="*60)
        
        self.connect_cloud_sql()
        self.connect_redis()
        
        stream_url = self._build_stream_url()
        logger.info(f"📡 Connecting to Binance WebSocket...")
        logger.info(f"📊 Streaming {len(self.symbols)} symbols")
        logger.info("-"*60)
        
        self.running = True
        message_count = 0
        
        while self.running:
            try:
                async with websockets.connect(stream_url, ping_interval=30) as ws:
                    logger.success("✅ WebSocket connected!")
                    
                    async for message in ws:
                        await self._handle_message(message)
                        message_count += 1
                        
                        if message_count % 1000 == 0:
                            logger.info(f"📨 Processed {message_count} messages")
                            
            except websockets.ConnectionClosed:
                logger.warning("⚠️ WebSocket disconnected, reconnecting...")
                await asyncio.sleep(self.reconnect_delay)
                
            except Exception as e:
                logger.error(f"❌ WebSocket error: {e}")
                await asyncio.sleep(self.reconnect_delay)
    
    def stop(self):
        """Stop the ingestor"""
        self.running = False
        if self.db_conn:
            self.db_conn.close()
        logger.info("🛑 WebSocket Ingestor stopped")


if __name__ == "__main__":
    ingestor = WebSocketIngestor()
    try:
        asyncio.run(ingestor.run())
    except KeyboardInterrupt:
        ingestor.stop()
