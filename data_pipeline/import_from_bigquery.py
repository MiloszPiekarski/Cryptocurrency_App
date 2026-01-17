from google.cloud import bigquery
from sqlalchemy import create_engine
import pandas as pd
import os
import sys

# DATABASE CONFIG (Matches your local Docker setup)
DB_USER = "postgres"
DB_PASS = "password123"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "turboplanx"

# BIGQUERY CONFIG (PLEASE UPDATE THESE)
# ---------------------------------------------------------
import os
BQ_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT") # Based on your Firebase config
BQ_DATASET_ID = "market_data"    # REPLACE with your actual dataset name
BQ_TABLE_ID = "crypto_prices"    # REPLACE with your actual table name
# ---------------------------------------------------------

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def import_bigquery_data():
    print("🚀 Starting Import from Google BigQuery to Local TimescaleDB...")
    
    try:
        # 1. Connect to Local DB
        engine = create_engine(DATABASE_URL)
        print("✅ Connected to Local TimescaleDB")

        # 2. Connect to BigQuery
        print(f"📡 Connecting to BigQuery Project: {BQ_PROJECT_ID}...")
        client = bigquery.Client(project=BQ_PROJECT_ID)

        # 3. Construct Query
        # We assume your BigQuery table has standard OHLCV columns: timestamp, symbol, open, high, low, close, volume
        # Adjust column names in the query below if yours are different
        query = f"""
            SELECT 
                timestamp,
                symbol,
                open,
                high,
                low,
                close,
                volume
            FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{BQ_TABLE_ID}`
            WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 365 DAY)
            ORDER BY timestamp ASC
        """
        
        print("📥 Executing Query...")
        query_job = client.query(query)
        
        # 4. Fetch to DataFrame
        df = query_job.to_dataframe()
        print(f"✅ Fetched {len(df)} rows from BigQuery")

        if df.empty:
            print("⚠️ No data found. Please check your Project/Dataset/Table IDs.")
            return

        # 5. Transform Data if needed
        # Ensure timestamp is datetime
        if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
            df['timestamp'] = pd.to_datetime(df['timestamp'])

        # 6. Load into Local DB
        print("💾 Saving to local 'ohlcv' table...")
        df.to_sql('ohlcv', engine, if_exists='append', index=False, method='multi')
        
        print("🎉 Import Complete! History is now available locally for High-Frequency Agents.")

    except Exception as e:
        print("\n❌ IMPORT FAILED")
        print(f"Error details: {e}")
        print("\nPossible fixes:")
        print("1. Check if 'gcloud auth application-default login' was run locally.")
        print("2. Verify BQ_DATASET_ID and BQ_TABLE_ID at the top of this script.")

if __name__ == "__main__":
    import_bigquery_data()
