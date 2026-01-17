"""
CASH MAELSTROM - Cloud SQL Data Sync
Populates Cloud SQL (Hot Storage) with historical OHLCV data from Binance.
"""

import ccxt
import psycopg2
from datetime import datetime
import time

from cloud_config import (
    CLOUD_SQL_IP, CLOUD_SQL_DATABASE, CLOUD_SQL_USER, CLOUD_SQL_PASSWORD,
    SUPPORTED_SYMBOLS, TIMEFRAMES
)

def sync_to_cloud_sql():
    print("="*60)
    print("CASH MAELSTROM - Cloud SQL Data Sync")
    print("="*60)
    
    # Connect to Cloud SQL
    print("🔌 Connecting to Cloud SQL...")
    conn = psycopg2.connect(
        host=CLOUD_SQL_IP,
        port=5432,
        dbname=CLOUD_SQL_DATABASE,
        user=CLOUD_SQL_USER,
        password=CLOUD_SQL_PASSWORD
    )
    conn.autocommit = True
    cursor = conn.cursor()
    print("✅ Connected!")
    
    # Connect to Binance
    exchange = ccxt.binance()
    
    print(f"📊 Syncing {len(SUPPORTED_SYMBOLS)} symbols × {len(TIMEFRAMES)} timeframes")
    print("-"*60)
    
    total_rows = 0
    
    for symbol in SUPPORTED_SYMBOLS:
        print(f"\n📈 {symbol}")
        
        for tf in TIMEFRAMES:
            try:
                # Fetch OHLCV from Binance
                ohlcv = exchange.fetch_ohlcv(symbol, tf, limit=500)
                
                if not ohlcv:
                    print(f"  ⚠️ {tf}: No data")
                    continue
                
                # Delete existing data for this symbol/timeframe
                cursor.execute("""
                    DELETE FROM ohlcv WHERE symbol = %s AND timeframe = %s
                """, (symbol, tf))
                
                # Insert fresh data
                for candle in ohlcv:
                    ts = datetime.fromtimestamp(candle[0] / 1000.0)
                    cursor.execute("""
                        INSERT INTO ohlcv (time, symbol, timeframe, open, high, low, close, volume)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT DO NOTHING
                    """, (ts, symbol, tf, candle[1], candle[2], candle[3], candle[4], candle[5]))
                
                total_rows += len(ohlcv)
                print(f"  ✅ {tf}: {len(ohlcv)} candles")
                
                time.sleep(0.2)  # Rate limit
                
            except Exception as e:
                print(f"  ❌ {tf}: {e}")
                
        time.sleep(0.5)
    
    cursor.close()
    conn.close()
    
    print("\n" + "="*60)
    print(f"🏁 COMPLETE! Total rows: {total_rows}")
    print("="*60)

if __name__ == "__main__":
    sync_to_cloud_sql()
