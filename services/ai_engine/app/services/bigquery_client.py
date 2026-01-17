from google.cloud import bigquery
import os
import pandas as pd
from typing import Optional

class BigQueryService:
    """
    CASH MAELSTROM: Long-Term Memory (BigQuery) Client.
    """
    def __init__(self):
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.dataset_id = "maelstrom" # Must match data_pipeline config
        
        try:
            self.client = bigquery.Client(project=self.project_id, location="US")
            self.enabled = True
            print(f"✅ BigQuery Connected: {self.project_id} (US)")
        except Exception as e:
            print(f"⚠️ BigQuery Init Failed: {e}")
            self.enabled = False

    def get_historical_trends(self, symbol: str, days: int = 30) -> Optional[pd.DataFrame]:
        """
        Fetch aggregated daily stats from BigQuery for long-term trend analysis.
        """
        if not self.enabled: return None

        query = f"""
            SELECT 
                DATE(time) as date,
                AVG(close) as avg_price,
                MIN(low) as min_price,
                MAX(high) as max_price,
                SUM(volume) as total_volume,
                STDDEV(close) as price_volatility
            FROM `{self.project_id}.{self.dataset_id}.market_history_cold`
            WHERE symbol = @symbol
            AND time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL @days DAY)
            GROUP BY date
            ORDER BY date ASC
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("symbol", "STRING", symbol),
                bigquery.ScalarQueryParameter("days", "INT64", days),
            ]
        )

        try:
            query_job = self.client.query(query, job_config=job_config)
            df = query_job.to_dataframe()
            if df.empty: return None
            return df
        except Exception as e:
            print(f"❌ [BQ] Read Error: {e}")
            return None

# Singleton
bq_service = BigQueryService()
