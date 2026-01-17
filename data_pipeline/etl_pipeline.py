"""
CASH MAELSTROM - ETL Pipeline (Layer 3: Data Lifecycle)
Moves data older than 48 hours from Cloud SQL (Hot) to BigQuery (Cold).

Schedule: Run daily at 3:00 AM via Cloud Scheduler
"""

from datetime import datetime, timedelta
import psycopg2
from google.cloud import bigquery
import pandas as pd
from loguru import logger

from cloud_config import (
    CLOUD_SQL_IP, CLOUD_SQL_DATABASE, CLOUD_SQL_USER, CLOUD_SQL_PASSWORD,
    BIGQUERY_TABLE_HISTORY, HOT_STORAGE_RETENTION_HOURS, GCP_PROJECT_ID
)

class ETLPipeline:
    """
    Extract-Transform-Load Pipeline
    
    Flow:
    1. EXTRACT: Get records older than 48h from Cloud SQL
    2. TRANSFORM: Clean and format for BigQuery
    3. LOAD: Insert into BigQuery
    4. CLEANUP: Delete archived records from Cloud SQL
    """
    
    def __init__(self):
        self.cloud_sql_conn = None
        self.bq_client = None
        self.retention_hours = HOT_STORAGE_RETENTION_HOURS
        
    def connect(self):
        """Initialize connections"""
        logger.info("🔌 Connecting to Cloud SQL...")
        self.cloud_sql_conn = psycopg2.connect(
            host=CLOUD_SQL_IP,
            port=5432,
            dbname=CLOUD_SQL_DATABASE,
            user=CLOUD_SQL_USER,
            password=CLOUD_SQL_PASSWORD
        )
        logger.success("✅ Cloud SQL connected!")
        
        logger.info("🔌 Connecting to BigQuery...")
        self.bq_client = bigquery.Client(project=GCP_PROJECT_ID)
        logger.success("✅ BigQuery connected!")
        
    def extract(self) -> pd.DataFrame:
        """Extract old records from Cloud SQL (Hot Storage)"""
        cutoff_time = datetime.now() - timedelta(hours=self.retention_hours)
        logger.info(f"📤 Extracting records older than {cutoff_time}")
        
        query = """
            SELECT time, symbol, price, volume, source
            FROM market_history
            WHERE time < %s
            ORDER BY time ASC
        """
        
        df = pd.read_sql(query, self.cloud_sql_conn, params=(cutoff_time,))
        logger.info(f"📦 Extracted {len(df)} records")
        
        return df
        
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform data for BigQuery schema"""
        if df.empty:
            return df
            
        # Rename/adjust columns for BigQuery
        df = df.rename(columns={'time': 'timestamp'})
        
        # Ensure proper types
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['price'] = df['price'].astype(float)
        df['volume'] = df['volume'].fillna(0).astype(float)
        
        logger.info(f"🔧 Transformed {len(df)} records for BigQuery")
        return df
        
    def load(self, df: pd.DataFrame):
        """Load data into BigQuery (Cold Storage)"""
        if df.empty:
            logger.info("📭 No data to load")
            return
            
        table_id = BIGQUERY_TABLE_HISTORY
        
        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_APPEND",
        )
        
        logger.info(f"📥 Loading {len(df)} records to BigQuery...")
        
        job = self.bq_client.load_table_from_dataframe(
            df, table_id, job_config=job_config
        )
        job.result()  # Wait for completion
        
        logger.success(f"✅ Loaded {len(df)} records to {table_id}")
        
    def cleanup(self, cutoff_time: datetime):
        """Delete archived records from Cloud SQL"""
        logger.info(f"🗑️ Cleaning up records older than {cutoff_time}")
        
        cursor = self.cloud_sql_conn.cursor()
        cursor.execute("""
            DELETE FROM market_history WHERE time < %s
        """, (cutoff_time,))
        
        deleted = cursor.rowcount
        self.cloud_sql_conn.commit()
        cursor.close()
        
        logger.success(f"🗑️ Deleted {deleted} records from Cloud SQL")
        
    def run(self):
        """Execute full ETL pipeline"""
        logger.info("="*60)
        logger.info("CASH MAELSTROM - ETL Pipeline (Hot → Cold)")
        logger.info("="*60)
        
        self.connect()
        
        cutoff_time = datetime.now() - timedelta(hours=self.retention_hours)
        
        # 1. EXTRACT
        df = self.extract()
        
        if df.empty:
            logger.info("✨ No old data to archive. Hot storage is clean!")
            return
            
        # 2. TRANSFORM
        df = self.transform(df)
        
        # 3. LOAD
        self.load(df)
        
        # 4. CLEANUP
        self.cleanup(cutoff_time)
        
        logger.success("🏁 ETL Pipeline Complete!")
        
    def close(self):
        if self.cloud_sql_conn:
            self.cloud_sql_conn.close()


if __name__ == "__main__":
    etl = ETLPipeline()
    try:
        etl.run()
    except Exception as e:
        logger.error(f"ETL failed: {e}")
    finally:
        etl.close()
