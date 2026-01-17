"""
TURBO-PLAN X - FULL DATA SYNC
Synchronizes all symbols and timeframes to TimescaleDB (Hot Storage)
"""

import ccxt
import pandas as pd
from sqlalchemy import create_engine, text
import time
from datetime import datetime

# Database
DB_URL = "postgresql://postgres:turboplanx_secure_password@localhost:5432/turboplanx"
engine = create_engine(DB_URL)

# All symbols for The Forge
SYMBOLS = [
    'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT',
    'ADA/USDT', 'AVAX/USDT', 'DOGE/USDT', 'DOT/USDT', 'TRX/USDT',
    'LINK/USDT', 'MATIC/USDT', 'LTC/USDT', 'SHIB/USDT', 'UNI/USDT',
    'ATOM/USDT', 'XLM/USDT', 'ETC/USDT', 'FIL/USDT', 'HBAR/USDT',
]

# Timeframes matching frontend buttons
TIMEFRAMES = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w']

def fetch_and_store(symbol, timeframe, limit=500):
    exchange = ccxt.binance()
    
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        
        if not ohlcv:
            print(f"  ⚠️ No data for {symbol} {timeframe}")
            return 0
            
        df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        df['symbol'] = symbol  # Keep with slash for consistency
        df['timeframe'] = timeframe
        
        # Use upsert logic - delete old, insert new
        with engine.connect() as conn:
            # Delete existing data for this symbol/timeframe to avoid duplicates
            conn.execute(text(f"""
                DELETE FROM ohlcv 
                WHERE symbol = :symbol AND timeframe = :tf
            """), {"symbol": symbol, "tf": timeframe})
            conn.commit()
        
        # Insert fresh data
        df.to_sql('ohlcv', engine, if_exists='append', index=False, method='multi')
        
        print(f"  ✅ {symbol} {timeframe}: {len(df)} candles")
        return len(df)
        
    except Exception as e:
        print(f"  ❌ {symbol} {timeframe}: {e}")
        return 0

def main():
    print("=" * 60)
    print("TURBO-PLAN X - FULL DATA SYNCHRONIZATION")
    print("=" * 60)
    print(f"Symbols: {len(SYMBOLS)}")
    print(f"Timeframes: {TIMEFRAMES}")
    print(f"Total jobs: {len(SYMBOLS) * len(TIMEFRAMES)}")
    print("-" * 60)
    
    total_rows = 0
    
    for symbol in SYMBOLS:
        print(f"\n📊 {symbol}")
        for tf in TIMEFRAMES:
            rows = fetch_and_store(symbol, tf)
            total_rows += rows
            time.sleep(0.3)  # Rate limit
        time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print(f"🏁 COMPLETE! Total rows inserted: {total_rows}")
    print("=" * 60)

if __name__ == "__main__":
    main()
