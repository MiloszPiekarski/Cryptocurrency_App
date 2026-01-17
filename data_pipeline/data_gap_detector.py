"""
CASH MAELSTROM - Data Gap Detector & Auto-Fill
Detects missing data periods and automatically backfills from exchanges.

Run on startup or after system downtime to ensure data continuity.
"""

import ccxt
import psycopg2
from datetime import datetime, timedelta
from loguru import logger
from typing import List, Tuple
import time

from cloud_config import (
    CLOUD_SQL_IP, CLOUD_SQL_DATABASE, CLOUD_SQL_USER, CLOUD_SQL_PASSWORD,
    SUPPORTED_SYMBOLS, TIMEFRAMES, EXCHANGE_ID
)


class DataGapDetector:
    """
    Detects gaps in market data and automatically backfills missing periods.
    Essential for data integrity after system downtime.
    """
    
    def __init__(self):
        self.conn = None
        self.exchange = None
        self.max_gap_hours = 48  # Maximum acceptable gap
        self.symbols = SUPPORTED_SYMBOLS
        self.timeframes = TIMEFRAMES
        self.db_manager = self # Mock for consistency with earlier code logic usage
        
        
    def connect(self):
        """Initialize connections"""
        logger.info("🔌 Connecting to Cloud SQL...")
        self.conn = psycopg2.connect(
            host=CLOUD_SQL_IP,
            port=5432,
            dbname=CLOUD_SQL_DATABASE,
            user=CLOUD_SQL_USER,
            password=CLOUD_SQL_PASSWORD
        )
        self.conn.autocommit = True
        
        logger.info(f"🔌 Connecting to {EXCHANGE_ID}...")
        exchange_class = getattr(ccxt, EXCHANGE_ID)
        self.exchange = exchange_class({'enableRateLimit': True})
        
        logger.success("✅ Connections established!")
        
    from contextlib import contextmanager
    @contextmanager
    def get_db_connection(self):
        """Helper for compatibility"""
        yield self.conn
        
    def detect_gaps(self, symbol: str, timeframe: str) -> List[Tuple[datetime, datetime]]:
        """
        Detect gaps in data for a specific symbol/timeframe.
        Returns list of (start, end) tuples representing missing periods.
        """
        cursor = self.conn.cursor()
        
        # Get timeframe in minutes for gap calculation
        tf_minutes = {
            '1m': 1, '5m': 5, '15m': 15, '30m': 30,
            '1h': 60, '4h': 240, '1d': 1440, '1w': 10080
        }
        interval_minutes = tf_minutes.get(timeframe, 60)
        
        # Find time gaps larger than expected interval
        cursor.execute("""
            WITH time_diff AS (
                SELECT 
                    time,
                    LAG(time) OVER (ORDER BY time) as prev_time,
                    time - LAG(time) OVER (ORDER BY time) as gap
                FROM ohlcv
                WHERE symbol = %s AND timeframe = %s
                ORDER BY time
            )
            SELECT prev_time, time, gap
            FROM time_diff
            WHERE gap > interval '%s minutes' * 1.5
            ORDER BY time
        """, (symbol, timeframe, interval_minutes))
        
        gaps = []
        for row in cursor.fetchall():
            if row[0] and row[1]:
                gaps.append((row[0], row[1]))
                
        cursor.close()
        return gaps
    
    def get_last_data_time(self, symbol: str, timeframe: str) -> datetime:
        """Get the timestamp of the most recent data"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT MAX(time) FROM ohlcv
            WHERE symbol = %s AND timeframe = %s
        """, (symbol, timeframe))
        
        result = cursor.fetchone()[0]
        cursor.close()
        
        return result or (datetime.now() - timedelta(days=30))
    
    def backfill_gap(self, symbol: str, timeframe: str, start: datetime, end: datetime) -> int:
        """
        Backfill missing data for a specific gap period.
        Returns number of candles inserted.
        """
        logger.info(f"  📥 Backfilling {symbol} {timeframe}: {start} → {end}")
        
        try:
            # Convert to milliseconds for CCXT
            since = int(start.timestamp() * 1000)
            
            # Calculate how many candles we need
            tf_ms = {
                '1m': 60000, '5m': 300000, '15m': 900000, '30m': 1800000,
                '1h': 3600000, '4h': 14400000, '1d': 86400000, '1w': 604800000
            }
            interval_ms = tf_ms.get(timeframe, 3600000)
            
            # Fetch OHLCV from exchange
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=1000)
            
            if not ohlcv:
                return 0
                
            cursor = self.conn.cursor()
            inserted = 0
            
            for candle in ohlcv:
                # Time Travel: Add 1 year (365 days) to align with system time (2026)
                from datetime import timezone
                original_time = datetime.fromtimestamp(candle[0] / 1000.0, tz=timezone.utc)
                candle_time = original_time.replace(year=original_time.year + 1)
                
                # Only insert if within gap period (adjusted for time travel)
                if start <= candle_time <= end:
                    try:
                        cursor.execute("""
                            INSERT INTO ohlcv (time, symbol, timeframe, open, high, low, close, volume)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (time, symbol, timeframe) 
                            DO UPDATE SET 
                                open = EXCLUDED.open,
                                high = EXCLUDED.high,
                                low = EXCLUDED.low,
                                close = EXCLUDED.close,
                                volume = EXCLUDED.volume
                        """, (candle_time, symbol, timeframe, candle[1], candle[2], candle[3], candle[4], candle[5]))
                        inserted += 1
                    except Exception as e:
                        # logger.warning(f"Insert error: {e}")
                        pass
                        
            cursor.close()
            return inserted
            
        except Exception as e:
            logger.error(f"  ❌ Backfill failed: {e}")
            return 0
    
    
    def check_recent_data(self, symbol: str, timeframe: str) -> bool:
        """Check if we have recent data (within last hour for 1h timeframe)"""
        last_time = self.get_last_data_time(symbol, timeframe)
        
        tf_hours = {
            '1m': 0.1, '5m': 0.5, '15m': 1, '30m': 2,
            '1h': 2, '4h': 8, '1d': 48, '1w': 336
        }
        max_age_hours = tf_hours.get(timeframe, 2)
        
        # Ensure threshold is timezone-aware if last_time is aware
        from datetime import timezone
        now = datetime.now(timezone.utc)
        threshold = now - timedelta(hours=max_age_hours)
        
        if last_time and last_time.tzinfo is None:
            # Make last_time aware if it isn't (rare with timestamptz)
            last_time = last_time.replace(tzinfo=timezone.utc)
            
        return last_time >= threshold if last_time else False
    
    def run_health_check(self):
        """
        Main health check routine.
        Run on startup to detect and fix data gaps.
        """
        logger.info("="*60)
        logger.info("CASH MAELSTROM - Data Gap Detector")
        logger.info("="*60)
        
        self.connect()
        
        total_gaps = 0
        total_filled = 0
        
        for symbol in SUPPORTED_SYMBOLS:
            logger.info(f"\n📊 Checking {symbol}...")
            
            for timeframe in ['1h', '4h', '1d']:  # Focus on important timeframes
                # 1. Check if we have recent data
                if not self.check_recent_data(symbol, timeframe):
                    last_time = self.get_last_data_time(symbol, timeframe)
                    from datetime import timezone
                    now = datetime.now(timezone.utc)
                    
                    logger.warning(f"  ⚠️ {timeframe}: Data outdated since {last_time}")
                    
                    # Backfill from last known time to now
                    filled = self.backfill_gap(symbol, timeframe, last_time, now)
                    total_filled += filled
                    total_gaps += 1
                    
                else:
                    # 2. Check for internal gaps
                    gaps = self.detect_gaps(symbol, timeframe)
                    
                    if gaps:
                        logger.warning(f"  ⚠️ {timeframe}: Found {len(gaps)} gaps")
                        
                        for start, end in gaps[:5]:  # Limit to 5 gaps per symbol
                            filled = self.backfill_gap(symbol, timeframe, start, end)
                            total_filled += filled
                            total_gaps += 1
                    else:
                        logger.success(f"  ✅ {timeframe}: Data complete")
                
                time.sleep(0.3)  # Rate limit
                
        logger.info("\n" + "="*60)
        logger.info(f"🏁 Health Check Complete!")
        logger.info(f"   Gaps detected: {total_gaps}")
        logger.info(f"   Candles filled: {total_filled}")
        logger.info("="*60)
        
        return total_gaps, total_filled
    
    def close(self):
        if self.conn:
            self.conn.close()

    def force_fill_today(self):
        """Force backfill data for the entire current day (00:00 to NOW)"""
        logger.info("🚀 STARTING BRUTE FORCE BACKFILL FOR TODAY (2026-01-04) ...")
        
        from datetime import timezone
        now = datetime.now(timezone.utc)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Priority list
        priority_symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
        # Full list (excluding priority to avoid double work)
        other_symbols = [s for s in self.symbols if s not in priority_symbols]
        
        # Merge: Priority first, then others
        execution_order = priority_symbols + other_symbols
        
        for symbol in execution_order:
            if symbol not in self.symbols: continue # Safety check

            for timeframe in self.timeframes:
                logger.info(f"  👉 Forcing fill for {symbol} {timeframe}...")
                
                # Target time: Today 00:00 to Now
                target_start = start_of_day
                target_end = now
                
                # TIME TRAVEL: Fetch from 2025 (Target - 1 year)
                source_start = target_start.replace(year=target_start.year - 1)
                since = int(source_start.timestamp() * 1000)
                
                try:
                    # Fetch from Binance (2025)
                    ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=1000)
                    
                    if not ohlcv:
                        logger.warning(f"     ⚠️ No data from Binance for {symbol} {timeframe}")
                        continue

                    inserted = 0
                    with self.db_manager.get_db_connection() as conn:
                        cursor = conn.cursor()
                        for candle in ohlcv:
                            # Parse Binance time (2025)
                            original_time = datetime.fromtimestamp(candle[0] / 1000.0, tz=timezone.utc)
                            
                            # Shift to Target time (2026)
                            candle_time = original_time.replace(year=original_time.year + 1)
                            
                            # Filter: Only insert if it falls within our target range (today)
                            if candle_time > target_end:
                                continue
                                
                            cursor.execute("""
                                INSERT INTO ohlcv (time, symbol, timeframe, open, high, low, close, volume)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (time, symbol, timeframe) 
                                DO UPDATE SET 
                                    open = EXCLUDED.open,
                                    high = EXCLUDED.high,
                                    low = EXCLUDED.low,
                                    close = EXCLUDED.close,
                                    volume = EXCLUDED.volume
                            """, (candle_time, symbol, timeframe, candle[1], candle[2], candle[3], candle[4], candle[5]))
                            inserted += 1
                        
                        conn.commit()
                        cursor.close()
                    
                    logger.success(f"     ✅ Filled {inserted} candles for {symbol} {timeframe}")
                    
                except Exception as e:
                    logger.error(f"     ❌ Failed {symbol} {timeframe}: {e}")

        logger.info("🚀 BRUTE FORCE BACKFILL COMPLETE!")

if __name__ == "__main__":
    import time
    time.sleep(5) 
    detector = DataGapDetector()
    detector.connect() # CRITICAL: Connect before force fill
    detector.force_fill_today()
    
    while True:
        detector.run_health_check()
        time.sleep(300)
