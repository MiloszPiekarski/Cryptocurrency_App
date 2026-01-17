"""
CASH MAELSTROM - Cloud Data Architecture Configuration
Layered Storage: Cloud SQL (Hot) + BigQuery (Cold)
"""

import os

# ============================================================
# GOOGLE CLOUD CONFIGURATION
# ============================================================

GCP_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")

# Cloud SQL - Hot Storage (Last 48 hours)
CLOUD_SQL_INSTANCE = os.getenv("CLOUD_SQL_INSTANCE")
CLOUD_SQL_IP = os.getenv("CLOUD_SQL_IP")
CLOUD_SQL_DATABASE = os.getenv("CLOUD_SQL_DATABASE")
CLOUD_SQL_USER = os.getenv("CLOUD_SQL_USER")
CLOUD_SQL_PASSWORD = os.getenv("CLOUD_SQL_PASSWORD")

if not CLOUD_SQL_PASSWORD or not CLOUD_SQL_IP:
    # Fallback/Warning (or raise error in strict mode)
    pass

CLOUD_SQL_CONNECTION_STRING = f"postgresql://{CLOUD_SQL_USER}:{CLOUD_SQL_PASSWORD}@{CLOUD_SQL_IP}:5432/{CLOUD_SQL_DATABASE}"

# BigQuery - Cold Storage (Historical Data)
BIGQUERY_DATASET = "market_data"
BIGQUERY_TABLE_PRICES = f"{GCP_PROJECT_ID}.{BIGQUERY_DATASET}.crypto_prices"
BIGQUERY_TABLE_HISTORY = f"{GCP_PROJECT_ID}.{BIGQUERY_DATASET}.market_history"

# Firebase - Real-time (Optional WOW Effect)
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")

# ============================================================
# DATA RETENTION POLICY
# ============================================================

HOT_STORAGE_RETENTION_HOURS = 48  # Data older than this moves to BigQuery
ETL_SCHEDULE_HOUR = 3  # Run ETL at 3:00 AM daily

# ============================================================
# EXCHANGE CONFIGURATION
# ============================================================

EXCHANGE_ID = "binance"
SUPPORTED_SYMBOLS = [
    'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT',
    'ADA/USDT', 'AVAX/USDT', 'DOGE/USDT', 'DOT/USDT', 'TRX/USDT',
    'LINK/USDT', 'MATIC/USDT', 'LTC/USDT', 'SHIB/USDT', 'UNI/USDT',
    'ATOM/USDT', 'XLM/USDT', 'ETC/USDT', 'FIL/USDT', 'HBAR/USDT',
]

TIMEFRAMES = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w']
