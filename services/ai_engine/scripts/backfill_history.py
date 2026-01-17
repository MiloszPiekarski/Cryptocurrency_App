import ccxt
import pandas as pd
from datetime import datetime, timedelta
import pg8000
import sqlalchemy
from google.cloud.sql.connector import Connector, IPTypes
import time
import sys

# Configuration
# Configuration
DB_URL = "postgresql://postgres:turboplanx_secure_password@localhost:5432/turboplanx"

# List of ~50 top crypto pairs
SYMBOLS = [
    'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'ADA/USDT', 'DOGE/USDT', 'AVAX/USDT', 'DOT/USDT', 
    'MATIC/USDT', 'SHIB/USDT', 'LTC/USDT', 'TRX/USDT', 'UNI/USDT', 'LINK/USDT', 'ATOM/USDT', 
    'XMR/USDT', 'ETC/USDT', 'BCH/USDT', 'XLM/USDT', 'ALGO/USDT', 'NEAR/USDT', 'FIL/USDT', 
    'VET/USDT', 'QNT/USDT', 'HBAR/USDT', 'ICP/USDT', 'SAND/USDT', 'MANA/USDT', 'AAVE/USDT', 
    'EGLD/USDT', 'AXS/USDT', 'THETA/USDT', 'EOS/USDT', 'XTZ/USDT', 'MKR/USDT', 'GRT/USDT', 
    'KLAY/USDT', 'NEO/USDT', 'CHZ/USDT', 'SNX/USDT', 'IOTA/USDT', 'ZEC/USDT', 'FTM/USDT', 
    'CAKE/USDT', 'RUNE/USDT', 'KSM/USDT', 'CRV/USDT', '1INCH/USDT', 'COMP/USDT', 'ZIL/USDT'
]

NOW = datetime.now()

TIMEFRAME_CONFIG = [
    {'label': '1M', 'api': 'M', 'start': datetime(2025, 1, 1)},
    {'label': '1w', 'api': 'W', 'start': datetime(2025, 1, 1)},
    {'label': '1d', 'api': 'D', 'start': datetime(2025, 1, 1)},
    {'label': '4h', 'api': '240', 'start': datetime(2025, 10, 1)},
    {'label': '1h', 'api': '60',  'start': datetime(2025, 10, 1)},
    {'label': '15m', 'api': '15', 'start': datetime(2025, 12, 1)},
    {'label': '5m',  'api': '5',  'start': datetime(2025, 12, 1)},
    {'label': '1m', 'api': '1', 'start': NOW - timedelta(days=3)} # Last 3 days for 1m to be fast
]

exchange = ccxt.bybit({'enableRateLimit': True})

def get_db_connection():
    return sqlalchemy.create_engine(DB_URL)

def get_completed_pairs(engine):
    """
    Check which (symbol, timeframe) pairs already have data in the database.
    Returns a set of tuples: {('BTC/USDT', '1h'), ('ETH/USDT', '1d'), ...}
    """
    try:
        with engine.connect() as conn:
            from sqlalchemy import text
            result = conn.execute(text("""
                SELECT DISTINCT symbol, timeframe 
                FROM ohlcv
            """))
            completed = {(row[0], row[1]) for row in result}
            print(f"✓ Found {len(completed)} already-completed (symbol, timeframe) pairs in database")
            return completed
    except Exception as e:
        print(f"Error checking completed pairs: {e}")
        return set()

def fetch_ohlcv(symbol, tf_config):
    start_dt = tf_config['start']
    label = tf_config['label']
    api_tf = tf_config['api']
    
    # print(f"Fetching {symbol} [{label}] since {start_dt}...")
    
    since = int(start_dt.timestamp() * 1000)
    all_ohlcv = []
    
    while True:
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, api_tf, since, limit=1000)
            if not ohlcv:
                break
            
            all_ohlcv.extend(ohlcv)
            next_start = ohlcv[-1][0] + 1
            
            if next_start <= since:
                break
                
            since = next_start
            
            now_ms = exchange.milliseconds()
            period_ms = (int(api_tf) * 60 * 1000) if api_tf.isdigit() else 86400000
            if ohlcv[-1][0] > now_ms - period_ms:
                 break
                 
            if len(ohlcv) < 1000:
                break
                
            time.sleep(0.1)
            
        except Exception as e:
            print(f"Error fetching {symbol} {label}: {e}")
            break
            
    # print(f"Fetched {len(all_ohlcv)} candles for {symbol} [{label}]")
    return all_ohlcv

def save_to_db(engine, symbol, label, candles):
    if not candles:
        return False

    df = pd.DataFrame(candles, columns=['timestamp_ms', 'open', 'high', 'low', 'close', 'volume'])
    df['symbol'] = symbol
    df['timeframe'] = label
    df['time'] = pd.to_datetime(df['timestamp_ms'], unit='ms')
    df['quote_volume'] = 0.0 # Placeholder
    df['trades_count'] = 0
    
    # Select columns matching schema
    df_final = df[['time', 'symbol', 'timeframe', 'open', 'high', 'low', 'close', 'volume', 'quote_volume', 'trades_count']]
    
    try:
        with engine.connect() as conn:
            from sqlalchemy import text
            stmt = text("""
                INSERT INTO ohlcv (time, symbol, timeframe, open, high, low, close, volume, quote_volume, trades_count)
                VALUES (:time, :symbol, :timeframe, :open, :high, :low, :close, :volume, :0, :0)
                ON CONFLICT (symbol, timeframe, time) 
                DO NOTHING
            """)
            
            # Use pandas generic to_sql for speed (or batch loop if needed)
            # But let's stick to the previous loop logic which is safer
            
            data = df_final.to_dict(orient='records')
            
            # Simple direct insert using pandas to_sql is often easier for bulk
            df_final.to_sql('ohlcv', engine, if_exists='append', index=False, method='multi', chunksize=1000)
                
            print(f"✓ Saved {len(data)} records for {symbol} {label}.")
            return True
        
    except Exception as e:
        # Retry with simpler method if method='multi' fails
        print(f"✗ DB Error (bulk): {e}")
        return False

def main():
    engine = get_db_connection()
    
    # SMART RESUME: Check what's already done
    completed_pairs = get_completed_pairs(engine)
    
    tasks = []
    for symbol in SYMBOLS:
        for tf in TIMEFRAME_CONFIG:
            # Skip if already in database
            if (symbol, tf['label']) in completed_pairs:
                continue
            tasks.append((symbol, tf))
    
    total_tasks = len(tasks)
    total_all = len(SYMBOLS) * len(TIMEFRAME_CONFIG)
    
    print(f"\n🚀 Starting Smart Backfill")
    print(f"📊 Total tasks: {total_all}")
    print(f"✓ Already completed: {len(completed_pairs)}")
    print(f"⏳ Remaining: {total_tasks}\n")
    
    if total_tasks == 0:
        print("✅ All data already downloaded!")
        return
    
    for idx, (symbol, tf) in enumerate(tasks, 1):
        print(f"\n[{idx}/{total_tasks}] Processing {symbol} {tf['label']}")
        
        data = fetch_ohlcv(symbol, tf)
        if data:
            success = save_to_db(engine, symbol, tf['label'], data)
            if success:
                completed_pairs.add((symbol, tf['label']))
    
    print(f"\n✅ Backfill Complete!")
    print(f"📈 Final count: {len(completed_pairs)}/{total_all} pairs")

if __name__ == "__main__":
    main()
