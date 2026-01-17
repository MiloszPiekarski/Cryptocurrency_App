"""
TURBO-PLAN X - Real-Time Market Data Streamer
Streams live cryptocurrency data from exchanges to Redis
"""

import asyncio
import json
import time
from typing import List, Dict, Optional
from datetime import datetime, timezone
from loguru import logger
import ccxt.async_support as ccxt_async
from database import db

class RealTimeStreamer:
    """
    Professional real-time market data streamer
    Uses polling (CCXT free) instead of WebSocket (requires ccxt.pro)
    """
    
    def __init__(self, exchange_name: str = 'binance', poll_interval: float = 1.0):
        self.exchange_name = exchange_name
        self.poll_interval = poll_interval
        self.exchange = None
        self.running = False
        
        # Track last prices for change detection
        self.last_prices: Dict[str, float] = {}
        
        logger.info(f"Initialized {exchange_name} streamer (poll interval: {poll_interval}s)")
    
    async def initialize(self):
        """Initialize async exchange connection"""
        exchange_class = getattr(ccxt_async, self.exchange_name)
        self.exchange = exchange_class({'enableRateLimit': True})
        logger.success(f"✓ {self.exchange_name} connection initialized")
    
    async def fetch_ticker(self, symbol: str) -> Optional[Dict]:
        """Fetch latest ticker data"""
        try:
            ticker = await self.exchange.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'last': ticker['last'],
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'high': ticker['high'],
                'low': ticker['low'],
                'volume': ticker['quoteVolume'],
                'change_24h': ticker.get('percentage', 0),
                'timestamp': ticker['timestamp'],
                'datetime': ticker['datetime']
            }
        except Exception as e:
            logger.warning(f"Error fetching ticker {symbol}: {e}")
            return None
    
    async def fetch_orderbook(self, symbol: str, limit: int = 10) -> Optional[Dict]:
        """Fetch order book depth"""
        try:
            orderbook = await self.exchange.fetch_order_book(symbol, limit=limit)
            return {
                'symbol': symbol,
                'bids': orderbook['bids'][:limit],
                'asks': orderbook['asks'][:limit],
                'timestamp': orderbook['timestamp']
            }
        except Exception as e:
            logger.warning(f"Error fetching orderbook {symbol}: {e}")
            return None
    
    async def stream_ticker_ws(self, symbol: str):
        """
        Stream ticker updates via WebSocket (Real-Time)
        Connects to Binance WS Stream for instant updates.
        Includes Exponential Backoff.
        """
        import aiohttp
        ws_symbol = symbol.replace('/', '').lower()
        ws_url = f"wss://stream.binance.com:9443/ws/{ws_symbol}@kline_1m"
        
        retry_delay = 1
        logger.info(f"Starting WebSocket stream for {symbol}: {ws_url}")

        while self.running:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.ws_connect(ws_url) as ws:
                        logger.success(f"✓ WebSocket connected for {symbol}")
                        retry_delay = 1 # Reset backoff
                        
                        async for msg in ws:
                            if not self.running: break
                            
                            data = json.loads(msg.data)
                            kline = data['k']
                            
                            # Standardize format to match our system
                            ticker_data = {
                                'symbol': symbol,
                                'last': float(kline['c']),
                                'bid': float(kline['c']), # Approx for kline stream
                                'ask': float(kline['c']), # Approx for kline stream
                                'high': float(kline['h']),
                                'low': float(kline['l']),
                                'volume': float(kline['v']),
                                'datetime': datetime.fromtimestamp(data['E']/1000).isoformat(),
                                'timestamp': data['E']
                            }
                            
                            # Publish to Redis (Hot Path)
                            redis_key = f"ticker:{symbol.replace('/', '')}"
                            db.redis_client.setex(redis_key, 120, json.dumps(ticker_data))
                            db.redis_client.publish('market:tickers', json.dumps(ticker_data))
                            db.redis_client.publish(f"ticker:{symbol.replace('/', '')}", json.dumps(ticker_data))
                            
                            # DB Buffer / check for save not implemented here to keep it simple,
                            # Relying on separate periodic task if needed, or this stream simply feeds Redis.
                            
            except Exception as e:
                logger.error(f"WebSocket Error {symbol}: {e}")
                logger.warning(f"Reconnecting in {retry_delay}s...")
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 60) # Max 60s backoff

    async def stream_ticker(self, symbol: str):
        """
        Legacy Polling Stream (Fallback)
        """
        # If BTC/USDT, redirect to WebSocket
        if symbol == 'BTC/USDT':
            await self.stream_ticker_ws(symbol)
            return

        logger.info(f"Starting ticker polling for {symbol}")
        
        while self.running:
            try:
                ticker_data = await self.fetch_ticker(symbol)
                
                if ticker_data:
                    current_price = ticker_data['last']
                    
                    # Store in Redis with longer TTL for less frequent updates
                    # Always store, even if price unchanged, to keep key alive
                    redis_key = f"ticker:{symbol.replace('/', '')}"
                    db.redis_client.setex(
                        redis_key,
                        120,  # Expire in 120 seconds (was 30, too short for 49 symbols)
                        json.dumps(ticker_data)
                    )
                    
                    # Publish to pub/sub channel
                    db.redis_client.publish(
                        'market:tickers',
                        json.dumps(ticker_data)
                    )
                    # Publish to SYMBOL SPECIFIC channel (Required for Frontend WS)
                    db.redis_client.publish(
                        f"ticker:{symbol.replace('/', '')}",
                        json.dumps(ticker_data)
                    )
                    
                    self.last_prices[symbol] = current_price
                
                # Sleep to respect rate limits
                await asyncio.sleep(self.poll_interval)
                
            except Exception as e:
                logger.error(f"Error in ticker stream {symbol}: {e}")
                await asyncio.sleep(5)
    
    async def stream_orderbook(self, symbol: str):
        """
        Stream orderbook updates to Redis
        """
        logger.info(f"Starting orderbook stream for {symbol}")
        
        while self.running:
            try:
                ob_data = await self.fetch_orderbook(symbol)
                
                if ob_data:
                    # Store in Redis (shorter expiry - more volatile data)
                    redis_key = f"orderbook:{symbol.replace('/', '')}"
                    db.redis_client.setex(
                        redis_key,
                        10,  # Expire in 10 seconds
                        json.dumps(ob_data)
                    )
                    
                    logger.debug(f"{symbol} orderbook: {len(ob_data['bids'])} bids, {len(ob_data['asks'])} asks")
                
                # Orderbook updates can be faster
                await asyncio.sleep(self.poll_interval * 2)
                
            except Exception as e:
                logger.error(f"Error in orderbook stream {symbol}: {e}")
                await asyncio.sleep(5)
    
    async def save_ticker_to_db(self, symbol: str):
        """
        Periodically save latest ticker as 1-minute candle to database
        Runs every minute
        """
        logger.info(f"Starting DB saver for {symbol}")
        
        while self.running:
            try:
                # Wait for next minute boundary
                now = datetime.now()
                seconds_until_next_minute = 60 - now.second
                await asyncio.sleep(seconds_until_next_minute)
                
                # Fetch ticker
                ticker_data = await self.fetch_ticker(symbol)
                
                if ticker_data:
                    # Save as 1-minute candle approximation
                    with db.get_connection() as conn:
                        cursor = conn.cursor()
                        
                        # Use ticker data as OHLC approximation
                        # (proper OHLC would need all trades in the minute)
                        timestamp = datetime.fromtimestamp(ticker_data['timestamp'] / 1000, tz=timezone.utc)
                        
                        cursor.execute('''
                            INSERT INTO ohlcv (time, symbol, timeframe, open, high, low, close, volume)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT DO NOTHING
                        ''', (
                            timestamp.replace(second=0, microsecond=0),  # Round to minute
                            symbol.replace('/', ''),
                            '1m',
                            ticker_data['last'],  # Approximation
                            ticker_data['high'],
                            ticker_data['low'],
                            ticker_data['last'],
                            ticker_data['volume']
                        ))
                        
                        cursor.close()
                        
                        logger.debug(f"Saved {symbol} 1m candle to DB")
                
            except Exception as e:
                logger.error(f"Error saving to DB {symbol}: {e}")
                await asyncio.sleep(60)
    
    async def stream_multiple_symbols(
        self,
        symbols: List[str],
        include_orderbook: bool = True,
        save_to_db: bool = True
    ):
        """
        Stream multiple symbols simultaneously
        """
        self.running = True
        
        tasks = []
        
        for symbol in symbols:
            # Ticker stream (always)
            tasks.append(self.stream_ticker(symbol))
            
            # Orderbook stream (optional)
            if include_orderbook:
                tasks.append(self.stream_orderbook(symbol))
            
            # DB saver (optional)
            if save_to_db:
                tasks.append(self.save_ticker_to_db(symbol))
        
        logger.success(f"✓ Started streaming {len(symbols)} symbols")
        logger.info(f"Ticker streams: {len(symbols)}")
        if include_orderbook:
            logger.info(f"Orderbook streams: {len(symbols)}")
        if save_to_db:
            logger.info(f"DB savers: {len(symbols)}")
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.warning("Received interrupt signal, shutting down...")
            self.running = False
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Clean shutdown"""
        logger.info("Shutting down streamer...")
        self.running = False
        
        if self.exchange:
            await self.exchange.close()
            logger.success("✓ Exchange connection closed")
        
        logger.success("✓ Streamer shutdown complete")


async def main():
    """
    Main entry point for real-time streaming
    """
    logger.info("="*60)
    logger.info("TURBO-PLAN X - Real-Time Market Data Streamer")
    logger.info("="*60)
    
    # Test database connection
    if not db.test_connection():
        logger.critical("Database connection failed! Exiting...")
        return
    
    # Initialize streamer - USING KUCOIN (Binance IP Banned)
    streamer = RealTimeStreamer(
        exchange_name='kucoin',
        poll_interval=2.0  # Poll every 2 seconds (slower for safety)
    )
    
    await streamer.initialize()
    
    # All 49 symbols with historical data
    # Prioritize by importance for orderbook & DB saving
    all_symbols = [
        # Top 10 - Full streaming (ticker + orderbook + DB)
        'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT',
        'ADA/USDT', 'AVAX/USDT', 'DOGE/USDT', 'DOT/USDT', 'LINK/USDT',
        
        # Top 11-30 - Ticker + DB only (no orderbook to save API calls)
        'TRX/USDT', 'TON/USDT', 'UNI/USDT', 'LTC/USDT', 'BCH/USDT', 'ATOM/USDT',
        'AAVE/USDT', 'XLM/USDT', 'FIL/USDT', 'HBAR/USDT', 'ETC/USDT',
        'APT/USDT', 'ARB/USDT', 'OP/USDT', 'NEAR/USDT', 'VET/USDT',
        'ALGO/USDT', 'GRT/USDT', 'FTM/USDT', 'SAND/USDT', 'MANA/USDT',
        
        # Top 31-49 - Ticker only (lightweight)
        'XTZ/USDT', 'THETA/USDT', 'AXS/USDT', 'EGLD/USDT', 'EOS/USDT',
        'KAVA/USDT', 'RUNE/USDT', 'FET/USDT', 'ROSE/USDT', 'LDO/USDT',
        'RNDR/USDT', 'IMX/USDT', 'CRV/USDT', 'MKR/USDT', 'SNX/USDT',
        'SUSHI/USDT', 'COMP/USDT', 'CHZ/USDT', 'SHIB/USDT'
    ]
    
    top_10_symbols = all_symbols[:10]  # Full features
    
    logger.info(f"Starting streams for {len(all_symbols)} symbols...")
    logger.info(f"  - FULL MODE: Streaming to Redis + DBSaving")
    logger.info("Press Ctrl+C to stop")
    logger.info("-"*60)
    
    # Start tasks
    tasks = []
    
    # Top 10: Full streaming
    for symbol in top_10_symbols:
        tasks.append(streamer.stream_ticker(symbol))
        # tasks.append(streamer.stream_orderbook(symbol)) # Optional: Disable OB for efficiency
        tasks.append(streamer.save_ticker_to_db(symbol)) # ENABLED
    
    # Others: Ticker + DB (Important for history)
    for symbol in all_symbols[10:]:
        tasks.append(streamer.stream_ticker(symbol))
        tasks.append(streamer.save_ticker_to_db(symbol)) # ENABLED
    
    logger.success(f"✓ Started {len(tasks)} total tasks")
    
    # Run all tasks
    streamer.running = True
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        logger.warning("Received interrupt signal, shutting down...")
        streamer.running = False
    finally:
        await streamer.shutdown()



if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n✓ Streamer stopped by user")
    finally:
        db.close_all()
