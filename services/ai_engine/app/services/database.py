import sqlalchemy
from google.cloud.sql.connector import Connector, IPTypes
import pg8000
import os
from dotenv import load_dotenv

load_dotenv()

# Cloud SQL Config 
# (Should ideally come from centralized config, but patching here for immediate fix)
project = os.getenv("GOOGLE_CLOUD_PROJECT")
region = "europe-central2"
instance = "maelstrom-db"
INSTANCE_CONNECTION_NAME = f"{project}:{region}:{instance}"
DB_USER = "postgres"
DB_PASS = "password123"
DB_NAME = "postgres"

def get_db_engine():
    connector = Connector()
    def getconn():
        return connector.connect(
            INSTANCE_CONNECTION_NAME,
            "pg8000",
            user=DB_USER,
            password=DB_PASS,
            db=DB_NAME,
            ip_type=IPTypes.PUBLIC
        )
    return sqlalchemy.create_engine("postgresql+pg8000://", creator=getconn)

# Global Engine Pool
engine = get_db_engine()

def get_ohlcv_from_db(symbol: str, timeframe: str = '1h', limit: int = 100):
    """
    Fetch OHLCV data from Cloud SQL.
    """
    try:
        # Normalize symbol
        symbol_normalized = symbol.upper()
        if '/' not in symbol_normalized and not symbol_normalized.endswith('USDT'):
             # Basic heuristic if plain 'BTC' is passed
             symbol_normalized = f"{symbol_normalized}/USDT"
        
        # Map frontend timeframes to DB defaults if needed
        # (The DB uses whatever string we inserted: '1min', '1h', etc.)
        
        query = sqlalchemy.text('''
            SELECT time, open, high, low, close, volume
            FROM ohlcv
            WHERE symbol = :symbol AND timeframe = :timeframe
            ORDER BY time DESC
            LIMIT :limit
        ''')
        
        with engine.connect() as conn:
            result = conn.execute(query, {
                "symbol": symbol_normalized, 
                "timeframe": timeframe, 
                "limit": limit
            })
            
            rows = result.fetchall()
            
            # Convert to dictionary format expected by API
            candles = [
                {
                    'time': int(row[0].timestamp() * 1000), # timestamp is first column
                    'open': float(row[1]),
                    'high': float(row[2]),
                    'low': float(row[3]),
                    'close': float(row[4]),
                    'volume': float(row[5])
                }
                for row in rows
            ]
            
            # Reverse for chronological order (oldest first) as usually expected by charting libs
            return list(reversed(candles))
            
    except Exception as e:
        print(f"Database error: {e}")
        return None
