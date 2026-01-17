"""
TURBO-PLAN X - ETL Lifecycle Manager
Manages the data flow between Hot (PostgreSQL) and Cold (BigQuery) storage.
Designed to be run as a daily cron job (Cloud Scheduler).
"""

import os
import time
from datetime import datetime, timedelta
import psycopg2
from google.cloud import bigquery
from loguru import logger
import pandas as pd
from sqlalchemy import create_engine

# Configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', 5432)
DB_NAME = os.getenv('POSTGRES_DB', 'turboplanx')
DB_USER = os.getenv('POSTGRES_USER', 'postgres')
DB_PASS = os.getenv('POSTGRES_PASSWORD', 'turboplanx_secure_password')

BQ_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
BQ_DATASET_ID = "market_data"
BQ_TABLE_ID = "crypto_prices"

HOT_DATA_RETENTION_HOURS = 48

def get_hot_db_engine():
    return create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

def move_hot_to_cold():
    """
    ETL Process:
    1. Extract data older than 48h from Postgres
    2. Load into BigQuery
    3. Delete from Postgres
    """
    logger.info("🚀 Starting ETL: Hot -> Cold Migration")
    
    try:
        engine = get_hot_db_engine()
        
        # 1. EXTRACT
        cutoff_time = datetime.now() - timedelta(hours=HOT_DATA_RETENTION_HOURS)
        logger.info(f"📅 Cutoff time: {cutoff_time}")
        
        query = f"SELECT * FROM ohlcv WHERE time < '{cutoff_time}'"
        df = pd.read_sql(query, engine)
        
        if df.empty:
            logger.info("✨ No data to migrate. Hot storage is clean.")
            return

        logger.info(f"📦 Extracting {len(df)} records for archival...")

        # 2. LOAD (to BigQuery)
        # Note: Requires 'google-cloud-bigquery' and authentication
        try:
            client = bigquery.Client(project=BQ_PROJECT_ID)
            table_ref = f"{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{BQ_TABLE_ID}"
            
            # Ensure table exists (simplified for script)
            # In prod, use Terraform or strict schemas
            
            job_config = bigquery.LoadJobConfig(
                write_disposition="WRITE_APPEND", # Append to history
            )
            
            job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
            job.result() # Wait for completion
            
            logger.success(f"✅ Successfully archived {len(df)} records to BigQuery")
            
        except Exception as bq_err:
            logger.error(f"❌ BigQuery Load Failed: {bq_err}")
            return # Stop here, don't delete data if archival failed

        # 3. TRANSFORM/CLEANUP (Delete from Hot)
        with engine.connect() as conn:
            delete_query = f"DELETE FROM ohlcv WHERE time < '{cutoff_time}'"
            result = conn.execute(delete_query)
            logger.info(f"🗑️ Cleaned {result.rowcount} records from Hot Storage")
            
        logger.success("🎉 ETL Process Complete!")

    except Exception as e:
        logger.error(f"❌ ETL Critical Failure: {e}")

if __name__ == "__main__":
    move_hot_to_cold()
