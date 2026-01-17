
from datetime import datetime, timedelta, timezone
import psycopg2
from google.cloud import bigquery
from datetime import datetime, timedelta, timezone
import psycopg2
from google.cloud import bigquery
from app.core.config import settings

import os

GCP_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
CLOUD_SQL_CONNECTION_STRING = settings.DATABASE_URL

class MarketDataFactory:
    """
    Singleton Factory for routing market data requests.
    - Recent Data (< 48h) -> Cloud SQL (Hot)
    - Historical Data (> 48h) -> BigQuery (Cold)
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MarketDataFactory, cls).__new__(cls)
            cls._instance.bq_client = bigquery.Client(project=GCP_PROJECT_ID)
            # PG Connection is created per request to avoid threading issues
        return cls._instance

    def get_ohlcv(self, symbol: str, timeframe: str, limit: int = 100):
        """
        Smart routing for OHLCV data.
        """
        # For simplicity, we currently fetch from Postgres as it holds the 'recent' backup.
        # But if we need 'deep' history that was archived, we check BQ.
        
        # Logic: 
        # 1. Try fetching from Cloud SQL first (it has the most granular recent data).
        # 2. If user requests data older than what's in SQL (e.g. > 48h/180days depending on retention), fetch from BQ.
        
        # For this stage, we assume Cloud SQL has the required data due to backfill.
        # But we prepare the structure for BQ fallback.
        
        return self._fetch_from_sql(symbol, timeframe, limit)

    def _fetch_from_sql(self, symbol: str, timeframe: str, limit: int):
        conn = psycopg2.connect(CLOUD_SQL_CONNECTION_STRING)
        cursor = conn.cursor()
        
        query = """
            SELECT time, open, high, low, close, volume 
            FROM ohlcv 
            WHERE symbol = %s AND timeframe = %s 
            ORDER BY time DESC 
            LIMIT %s
        """
        cursor.execute(query, (symbol, timeframe, limit))
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to dictionary/object list
        data = []
        for r in rows: # Reverse to chronological order if needed, but DESC is standard for "last N"
            data.append({
                "time": r[0].isoformat(),
                "open": float(r[1]),
                "high": float(r[2]),
                "low": float(r[3]),
                "close": float(r[4]),
                "volume": float(r[5])
            })
        return data

    def _fetch_from_bigquery(self, symbol: str, timeframe: str, limit: int):
        # Implementation for ETAP 2 Cold Storage
        query = f"""
            SELECT time, open, high, low, close, volume
            FROM `{GCP_PROJECT_ID}.maelstrom.market_history_cold`
            WHERE symbol = '{symbol}' AND timeframe = '{timeframe}'
            ORDER BY time DESC
            LIMIT {limit}
        """
        query_job = self.bq_client.query(query)
        return [dict(row) for row in query_job]

market_factory = MarketDataFactory()
