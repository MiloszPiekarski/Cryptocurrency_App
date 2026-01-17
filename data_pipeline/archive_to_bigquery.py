
import os
import logging
import psycopg2
from google.cloud import bigquery
from datetime import datetime, timedelta, timezone
from cloud_config import CLOUD_SQL_CONNECTION_STRING, GCP_PROJECT_ID

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

# Config
DATASET_ID = "maelstrom"
TABLE_ID = "market_history_cold"
RETENTION_HOURS = 48 

def get_bq_client():
    return bigquery.Client(project=GCP_PROJECT_ID)

def ensure_bq_schema(client):
    dataset_ref = client.dataset(DATASET_ID)
    try:
        client.get_dataset(dataset_ref)
    except Exception:
        logger.info(f"Creating dataset {DATASET_ID}...")
        client.create_dataset(bigquery.Dataset(dataset_ref))

    table_ref = dataset_ref.table(TABLE_ID)
    try:
        client.get_table(table_ref)
    except Exception:
        logger.info(f"Creating table {TABLE_ID}...")
        schema = [
            bigquery.SchemaField("time", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("timeframe", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("open", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("high", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("low", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("close", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("volume", "FLOAT", mode="REQUIRED"),
        ]
        table = bigquery.Table(table_ref, schema=schema)
        # Partition by time for efficiency
        table.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="time"
        )
        client.create_table(table)

def archive_and_prune():
    logger.info("📦 STARTING ARCHIVAL PROCESS (Hot -> Cold)")
    
    # 1. Connect to SQL
    conn = psycopg2.connect(CLOUD_SQL_CONNECTION_STRING)
    cursor = conn.cursor()
    
    # 2. Identify Cold Data (> 48h)
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=RETENTION_HOURS)
    logger.info(f"   Cutoff Time: {cutoff_time}")
    
    query_select = """
        SELECT time, symbol, timeframe, open, high, low, close, volume 
        FROM ohlcv 
        WHERE time < %s
        LIMIT 50000 
    """
    # Use LIMIT to avoid OOM, run frequently
    
    cursor.execute(query_select, (cutoff_time,))
    rows = cursor.fetchall()
    
    if not rows:
        logger.info("   ✅ No data to archive.")
        conn.close()
        return

    logger.info(f"   Found {len(rows)} records to archive. Uploading to BigQuery...")
    
    # 3. Upload to BQ
    client = get_bq_client()
    ensure_bq_schema(client)
    
    table_ref = client.dataset(DATASET_ID).table(TABLE_ID)
    
    # Convert to JSON/Dict for streaming insert
    rows_to_insert = [
        {
            "time": r[0].isoformat(),
            "symbol": r[1],
            "timeframe": r[2],
            "open": float(r[3]),
            "high": float(r[4]),
            "low": float(r[5]),
            "close": float(r[6]),
            "volume": float(r[7]),
        }
        for r in rows
    ]
    
    errors = client.insert_rows_json(table_ref, rows_to_insert)
    
    if errors:
        logger.error(f"   ❌ BigQuery Insert Errors: {errors}")
        conn.close()
        return # Do not delete if upload failed
        
    logger.info("   ✅ Upload successful. Pruning Cloud SQL...")
    
    # 4. Prune from SQL
    # Using specific IDs or timeframe? 
    # Delete exactly what we selected.
    # Safe way: Delete where time < cutoff.
    # Note: If concurrent inserts happened with time < cutoff, they might be deleted without archive.
    # Ideally use IDs. But ohlcv doesn't have ID column in standard schema shown.
    # We'll use (time, symbol, timeframe) composite key validation or just Delete < cutoff.
    # Given the volume, Delete < cutoff is standard practice for Retention Policy.
    
    query_delete = "DELETE FROM ohlcv WHERE time < %s"
    cursor.execute(query_delete, (cutoff_time,))
    conn.commit()
    deleted_count = cursor.rowcount
    
    logger.info(f"   🗑️  Pruned {deleted_count} records from Hot Storage.")
    conn.close()

if __name__ == "__main__":
    archive_and_prune()
