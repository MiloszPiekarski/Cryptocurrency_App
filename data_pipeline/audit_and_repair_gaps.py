
import os
import sys
import psycopg2
import ccxt
import time
from datetime import datetime, timedelta, timezone
from loguru import logger

# Add project root to path to import backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import config
try:
    from backend.app.core.config import settings
    try:
        from data_pipeline.cloud_config import SUPPORTED_SYMBOLS, TIMEFRAMES
    except ImportError:
        # Fallback if import fails
        SUPPORTED_SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT', 'ADA/USDT']
        TIMEFRAMES = ['1h', '4h', '1d']

    DB_URL = settings.DATABASE_URL
    if not DB_URL or "turboplanx" not in DB_URL:
         # Force the one used by backend
         DB_URL = "postgresql://postgres:turboplanx_secure_password@localhost:5432/turboplanx"
except Exception as e:
    logger.warning(f"Could not load backend settings ({e}). Using Turboplanx fallback...")
    DB_URL = "postgresql://postgres:turboplanx_secure_password@localhost:5432/turboplanx"
    SUPPORTED_SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT']
    TIMEFRAMES = ['1h', '4h', '1d']

# Setup Logger
logger.add("gap_repair.log", rotation="1 MB")

def get_db_connection():
    return psycopg2.connect(DB_URL)

def audit_and_repair(symbol='BTC/USDT', timeframe='1h', hours_back=336):
    
    # Delta calculation
    tf_delta = None
    if timeframe == '1m': tf_delta = timedelta(minutes=1)
    elif timeframe == '5m': tf_delta = timedelta(minutes=5)
    elif timeframe == '15m': tf_delta = timedelta(minutes=15)
    elif timeframe == '30m': tf_delta = timedelta(minutes=30)
    elif timeframe == '1h': tf_delta = timedelta(hours=1)
    elif timeframe == '4h': tf_delta = timedelta(hours=4)
    elif timeframe == '1d': tf_delta = timedelta(days=1)
    elif timeframe == '1w': tf_delta = timedelta(weeks=1)
    
    logger.info(f"🔍 Starting Audit for {symbol} ({timeframe}) - Last {hours_back} hours")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return
    
    # 1. Fetch existing data
    now = datetime.now(timezone.utc)
    end_time = now.replace(second=0, microsecond=0)
    if timeframe == '1h': end_time = end_time.replace(minute=0)
    
    start_time = end_time - timedelta(hours=hours_back)
    
    # Adjust start time to align with timeframe? (Optional, but good for clean check)
    
    query = """
        SELECT time FROM ohlcv 
        WHERE (symbol = %s OR symbol = %s) AND timeframe = %s AND time >= %s AND time < %s
        ORDER BY time ASC
    """
    cursor.execute(query, (symbol, symbol.replace('/', ''), timeframe, start_time, end_time))
    rows = cursor.fetchall()
    existing_times = {row[0].replace(tzinfo=timezone.utc) for row in rows}
    
    # 2. Identify Gaps
    expected_time = start_time
    missing_blocks = [] # List of (start_ts, end_ts) tuples for bulk fetch
    
    current_gap_start = None
    
    while expected_time < end_time:
        if expected_time not in existing_times and expected_time < now:
             if current_gap_start is None:
                 current_gap_start = expected_time
        else:
             if current_gap_start is not None:
                 # Gap ended
                 missing_blocks.append((current_gap_start, expected_time))
                 current_gap_start = None
        
        expected_time += tf_delta
    
    # Close pending gap
    if current_gap_start is not None:
        missing_blocks.append((current_gap_start, end_time))
        
    logger.info(f"📊 Audit Complete. Found {len(missing_blocks)} gap blocks.")
    
    if not missing_blocks:
        logger.success(f"✨ {symbol} {timeframe}: Zero Gaps found.")
        cursor.close()
        conn.close()
        return

    # 3. Bulk Repair
    # Use KuCoin (Binance IP banned) with Binance fallback
    exchange = ccxt.kucoin()
    exchange_fallback = ccxt.binance()
    total_repaired = 0
    
    for gap_start, gap_end in missing_blocks:
        logger.info(f"🚑 REPAIRING BLOCK: {gap_start} -> {gap_end}")
        
        current_fetch_start = gap_start
        
        while current_fetch_start < gap_end:
            try:
                since_ms = int(current_fetch_start.timestamp() * 1000)
                # Max limit 1000 usually
                candles = exchange.fetch_ohlcv(symbol, timeframe, since=since_ms, limit=1000)
                
                if not candles:
                    logger.warning(f"⚠️ No data from exchange for {current_fetch_start}")
                    break
                
                # Insert batch
                args_list = []
                for c in candles:
                    c_dt = datetime.fromtimestamp(c[0]/1000, tz=timezone.utc)
                    if c_dt >= gap_end: break # Don't overshoot
                    
                    args_list.append((c_dt, symbol, timeframe, c[1], c[2], c[3], c[4], c[5]))
                    # Also normalized
                    args_list.append((c_dt, symbol.replace('/', ''), timeframe, c[1], c[2], c[3], c[4], c[5]))
                
                if not args_list:
                    break

                # Bulk Insert (Plain, ignore errors individually or use executemany)
                # executemany with ignore duplicate might be complex in raw SQL without ON CONFLICT DO NOTHING (which failed)
                # But we know these are gaps. So duplicates unlikely unless partial data exists.
                # We'll stick to loop for safety or simple executemany with try/except around block?
                # Let's simple loop to be safe with the constraint issue
                
                for args in args_list:
                     try:
                        cursor.execute("""
                            INSERT INTO ohlcv (time, symbol, timeframe, open, high, low, close, volume)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, args)
                        total_repaired += 1
                     except Exception:
                        pass # Ignore duplicates/constraint errors
                
                conn.commit()
                
                # Advance fetch pointer
                last_candle_time = datetime.fromtimestamp(candles[-1][0]/1000, tz=timezone.utc)
                current_fetch_start = last_candle_time + tf_delta
                
                # Check if we are done with this block
                if current_fetch_start >= gap_end or len(candles) < 1000:
                    break
                    
                time.sleep(2.0) # Rate limit INCREASED to avoid 418 IP Ban
                
            except Exception as e:
                logger.error(f"Fetch/Insert Error: {e}")
                time.sleep(5) # Backoff on error
                break
                
    logger.success(f"✅ Repaired {total_repaired} candles for {symbol} {timeframe}")
    cursor.close()
    conn.close()

def run_all():
    logger.info("🚀 STARTING GLOBAL REPAIR 🚀")
    
    # Prioritize 1h, 4h, 1d first
    priority_tfs = ['1h', '4h', '1d']
    other_tfs = [tf for tf in TIMEFRAMES if tf not in priority_tfs]
    
    # Process Priority Timeframes
    for tf in priority_tfs:
        for symbol in SUPPORTED_SYMBOLS:
            audit_and_repair(symbol, tf, hours_back=336) # 14 days
            
    # Process Others (shorter lookback for 1m to save time? Maybe 24h?)
    for tf in other_tfs:
        lookback = 336
        if tf == '1m': lookback = 48 # Only 48h for 1m to avoid waiting forever
        
        for symbol in SUPPORTED_SYMBOLS:
            audit_and_repair(symbol, tf, hours_back=lookback)
            
    logger.success("🏁 GLOBAL REPAIR COMPLETED 🏁")

if __name__ == "__main__":
    run_all()
