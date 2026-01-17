import ccxt
import time
from datetime import datetime, timedelta, timezone
import psycopg2
from cloud_config import CLOUD_SQL_CONNECTION_STRING, SUPPORTED_SYMBOLS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
TARGET_END_DATE = datetime.now(timezone.utc)
# Focus symbols first for immediate relief
PRIORITY_SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
# The user wants "as professional platform", so let's do more if possible
OTHER_SYMBOLS = [s for s in SUPPORTED_SYMBOLS if s not in PRIORITY_SYMBOLS]
ALL_SYMBOLS = PRIORITY_SYMBOLS + OTHER_SYMBOLS

TIMEFRAME_CONFIG = {
    '1m':  timedelta(days=90),
    '5m':  timedelta(days=90),
    '15m': timedelta(days=90),
    '30m': timedelta(days=90),
    '1h':  timedelta(days=180),
    '4h':  timedelta(days=180),
    '1d':  timedelta(days=365),
    '1w':  timedelta(days=365),
    '1M':  timedelta(days=365*5)
}

def connect_db():
    return psycopg2.connect(CLOUD_SQL_CONNECTION_STRING)

def rebuild_history():
    conn = connect_db()
    cursor = conn.cursor()
    
    logger.info("🗑️ PURGING ALL OHLCV DATA (CLEAN SLATE)...")
    cursor.execute("TRUNCATE TABLE ohlcv")
    conn.commit()
    logger.info("✅ Database purged.")

    exchange = ccxt.binance()
    
    for symbol in ALL_SYMBOLS:
        logger.info(f"🏙️  PROCESSING SYMBOL: {symbol}")
        
        for tf, delta in TIMEFRAME_CONFIG.items():
            logger.info(f"   🚀 BACKFILL {tf} (Range: {delta.days} days)...")
            
            target_start = TARGET_END_DATE - delta
            current_iter_date = target_start
            
            inserted_count = 0
            while current_iter_date < TARGET_END_DATE:
                source_fetch_date = current_iter_date - timedelta(days=365)
                since_ts = int(source_fetch_date.timestamp() * 1000)
                
                try:
                    ohlcv = exchange.fetch_ohlcv(symbol, tf, since=since_ts, limit=1000)
                    
                    if not ohlcv:
                        current_iter_date += timedelta(days=1)
                        continue

                    records = []
                    last_candle_ts = 0
                    
                    for candle in ohlcv:
                        raw_ts = candle[0]
                        last_candle_ts = raw_ts
                        dt_object = datetime.fromtimestamp(raw_ts / 1000, tz=timezone.utc)
                        
                        try:
                            sim_dt = dt_object.replace(year=dt_object.year + 1)
                        except ValueError:
                            # Handle Feb 29
                            sim_dt = dt_object.replace(year=dt_object.year + 1, day=28)
                        
                        if sim_dt > TARGET_END_DATE:
                            continue
                            
                        records.append((sim_dt, symbol, tf, candle[1], candle[2], candle[3], candle[4], candle[5]))

                    if records:
                        # Batch Insert
                        args_str = ','.join(cursor.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s)", x).decode('utf-8') for x in records)
                        cursor.execute(f"INSERT INTO ohlcv (time, symbol, timeframe, open, high, low, close, volume) VALUES {args_str} ON CONFLICT DO NOTHING")
                        conn.commit()
                        inserted_count += len(records)
                    
                    if not records and ohlcv:
                        # All fetched candles were in future relative to Sim
                        break
                    
                    # Update iterator based on last fetched candle source time
                    last_dt_source = datetime.fromtimestamp(last_candle_ts / 1000, tz=timezone.utc)
                    next_source_date = last_dt_source + timedelta(milliseconds=1)
                    current_iter_date = next_source_date.replace(year=next_source_date.year + 1)
                    
                    # Very small sleep to respect API but stay fast
                    time.sleep(0.05) 
                    
                except Exception as e:
                    logger.error(f"      ❌ Error {tf}: {e}")
                    time.sleep(1)
                    current_iter_date += timedelta(hours=1)
            
            logger.info(f"      ✅ OK: {inserted_count} rows.")

    conn.close()
    logger.info("🎉 DEEP REBUILD COMPLETE FOR ALL SYMBOLS.")

if __name__ == "__main__":
    rebuild_history()
