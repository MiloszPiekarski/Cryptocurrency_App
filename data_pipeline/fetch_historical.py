import ccxt
import pandas as pd
from sqlalchemy import create_engine
import time
from datetime import datetime
import os

# Konfiguracja Bazy (Hardcoded for MVP reliability based on Docker setup)
DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

def fetch_and_store(symbol, timeframe='1h', limit=1000):
    print(f"📥 Fetching {symbol} ({timeframe})...")
    
    exchange = ccxt.binance()
    
    try:
        # Fetch OHLCV
        ochlv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        
        # DataFrame
        df = pd.DataFrame(ochlv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        df['symbol'] = symbol
        df['timeframe'] = timeframe
        
        # Save to DB
        # TimescaleDB is PostgreSQL compatible. We append data.
        # Note: In production we should handle duplicates (upsert), but for init 'append' is fine.
        df.to_sql('ohlcv', engine, if_exists='append', index=False, method='multi')
        
        print(f"✅ Stored {len(df)} rows for {symbol}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    symbols = [
        'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT',
        'ADA/USDT', 'AVAX/USDT', 'DOGE/USDT', 'DOT/USDT', 'TRX/USDT',
        'LINK/USDT', 'MATIC/USDT', 'LTC/USDT', 'SHIB/USDT', 'UNI/USDT',
        'ATOM/USDT', 'XLM/USDT', 'ETC/USDT', 'FIL/USDT', 'HBAR/USDT',
        'APT/USDT', 'ARB/USDT', 'NEAR/USDT', 'VET/USDT', 'LDO/USDT',
        'QNT/USDT', 'AAVE/USDT', 'GRT/USDT', 'OP/USDT', 'ALGO/USDT',
        'STX/USDT', 'EOS/USDT', 'XTZ/USDT', 'IMX/USDT', 'SAND/USDT',
        'EGLD/USDT', 'THETA/USDT', 'FTM/USDT', 'MANA/USDT', 'AXS/USDT',
        'SNX/USDT', 'FLOW/USDT', 'KAVA/USDT', 'MINA/USDT', 'GALA/USDT',
        'CHZ/USDT', 'RUNE/USDT', 'PEPE/USDT', 'SUI/USDT', 'TIA/USDT'
    ]
    
    # Timeframes required by the frontend
    timeframes = ['1d', '1w', '4h', '1h', '15m']
    
    print(f"🚀 Starting Historical Data Ingestion for {len(symbols)} symbols and {len(timeframes)} timeframes...")
    
    for s in symbols:
        print(f"=== Processing {s} ===")
        for tf in timeframes:
            fetch_and_store(s, timeframe=tf, limit=1000)
            time.sleep(0.5) # Rate limit safety per request
        
        time.sleep(1) # Extra safety between symbols
    
    print("🏁 Ingestion Complete.")
    
    print("🏁 Ingestion Complete.")
