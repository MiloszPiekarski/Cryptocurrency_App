"""
CASH MAELSTROM - Cloud SQL Schema Setup
Creates the market_history table in Google Cloud SQL (Hot Storage)
"""

import psycopg2
from cloud_config import CLOUD_SQL_CONNECTION_STRING, CLOUD_SQL_IP, CLOUD_SQL_DATABASE, CLOUD_SQL_USER, CLOUD_SQL_PASSWORD

def create_schema():
    print("🔧 Connecting to Cloud SQL (maelstrom-db)...")
    
    try:
        conn = psycopg2.connect(
            host=CLOUD_SQL_IP,
            port=5432,
            dbname=CLOUD_SQL_DATABASE,
            user=CLOUD_SQL_USER,
            password=CLOUD_SQL_PASSWORD,
            connect_timeout=10
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("✅ Connected to Cloud SQL!")
        
        # Create market_history table (Hot Storage - last 48h)
        print("📋 Creating market_history table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_history (
                id SERIAL,
                time TIMESTAMPTZ NOT NULL,
                symbol VARCHAR(20) NOT NULL,
                price DOUBLE PRECISION NOT NULL,
                volume DOUBLE PRECISION,
                source VARCHAR(50) DEFAULT 'binance',
                PRIMARY KEY (id)
            );
        """)
        
        # Create indices for fast queries
        print("📋 Creating indices...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_market_history_symbol_time 
            ON market_history (symbol, time DESC);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_market_history_time 
            ON market_history (time DESC);
        """)
        
        # Create ohlcv table for candlestick data
        print("📋 Creating ohlcv table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ohlcv (
                id SERIAL,
                time TIMESTAMPTZ NOT NULL,
                symbol VARCHAR(20) NOT NULL,
                timeframe VARCHAR(10) NOT NULL,
                open DOUBLE PRECISION NOT NULL,
                high DOUBLE PRECISION NOT NULL,
                low DOUBLE PRECISION NOT NULL,
                close DOUBLE PRECISION NOT NULL,
                volume DOUBLE PRECISION NOT NULL,
                PRIMARY KEY (id),
                UNIQUE (time, symbol, timeframe)
            );
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ohlcv_symbol_tf_time 
            ON ohlcv (symbol, timeframe, time DESC);
        """)
        
        print("✅ Schema created successfully in Cloud SQL!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    create_schema()
