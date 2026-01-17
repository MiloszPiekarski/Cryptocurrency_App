"""
CASH MAELSTROM - Statistics Module (Layer: The Muscle)
Smart routing between Hot Storage (Cloud SQL) and Cold Storage (BigQuery).

Implements the variance formula: σ² = (1/n) Σ(xi - μ)²
"""

import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from loguru import logger
import psycopg2
from google.cloud import bigquery

# Cloud SQL configuration
CLOUD_SQL_IP = os.getenv("CLOUD_SQL_IP")
CLOUD_SQL_DATABASE = "maelstrom"
CLOUD_SQL_USER = "postgres"
CLOUD_SQL_PASSWORD = os.getenv("CLOUD_SQL_PASSWORD")
CLOUD_SQL_CONNECTION_NAME = "maelstrom-db"

# BigQuery configuration
import os

GCP_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
BIGQUERY_TABLE = f"{GCP_PROJECT_ID}.market_data.market_history"

# Hot/Cold boundary
HOT_STORAGE_HOURS = 48


class StatisticsModule:
    """
    Layer: The Muscle
    
    Smart data routing:
    - Recent data (< 48h) -> Cloud SQL (Hot Storage)
    - Historical data (> 48h) -> BigQuery (Cold Storage)
    
    Implements statistical calculations including variance (σ²).
    """
    
    def __init__(self):
        self.bq_client = None
        
    def _get_cloud_sql_connection(self):
        """Get connection to Cloud SQL (Hot Storage)"""
        return psycopg2.connect(
            host=CLOUD_SQL_IP,
            port=5432,
            dbname=CLOUD_SQL_DATABASE,
            user=CLOUD_SQL_USER,
            password=CLOUD_SQL_PASSWORD
        )
        
    def _get_bq_client(self):
        """Get BigQuery client (Cold Storage)"""
        if not self.bq_client:
            try:
                self.bq_client = bigquery.Client(project=GCP_PROJECT_ID)
            except Exception as e:
                logger.warning(f"BigQuery unavailable: {e}")
        return self.bq_client
    
    async def get_price_data(
        self, 
        symbol: str, 
        start_time: datetime, 
        end_time: datetime
    ) -> List[float]:
        """
        Fetch price data with smart Hot/Cold routing.
        
        - If range is within 48h: Query Cloud SQL only
        - If range spans beyond 48h: Query both and merge
        """
        now = datetime.now()
        hot_threshold = now - timedelta(hours=HOT_STORAGE_HOURS)
        
        prices = []
        
        # Determine routing
        if start_time >= hot_threshold:
            # All data is in Hot Storage
            prices = self._fetch_from_cloud_sql(symbol, start_time, end_time)
            logger.debug(f"📊 {symbol}: Fetched {len(prices)} from HOT (Cloud SQL)")
            
        elif end_time < hot_threshold:
            # All data is in Cold Storage
            prices = self._fetch_from_bigquery(symbol, start_time, end_time)
            logger.debug(f"🧊 {symbol}: Fetched {len(prices)} from COLD (BigQuery)")
            
        else:
            # Hybrid: Some in Hot, some in Cold
            cold_prices = self._fetch_from_bigquery(symbol, start_time, hot_threshold)
            hot_prices = self._fetch_from_cloud_sql(symbol, hot_threshold, end_time)
            prices = cold_prices + hot_prices
            logger.debug(f"🔀 {symbol}: Fetched {len(cold_prices)} COLD + {len(hot_prices)} HOT")
            
        return prices
    
    def _fetch_from_cloud_sql(
        self, 
        symbol: str, 
        start: datetime, 
        end: datetime
    ) -> List[float]:
        """Query Cloud SQL (Hot Storage)"""
        try:
            conn = self._get_cloud_sql_connection()
            cursor = conn.cursor()
            
            # Support both formats: BTCUSDT and BTC/USDT
            symbol_no_slash = symbol.replace('/', '')
            symbol_with_slash = symbol if '/' in symbol else f"{symbol[:-4]}/{symbol[-4:]}" if len(symbol) > 5 else symbol
            
            cursor.execute("""
                SELECT price FROM market_history
                WHERE (symbol = %s OR symbol = %s) AND time BETWEEN %s AND %s
                ORDER BY time ASC
            """, (symbol_no_slash, symbol_with_slash, start, end))
            
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            
            return [float(r[0]) for r in rows]
            
        except Exception as e:
            logger.error(f"Cloud SQL query failed: {e}")
            return []
    
    def _fetch_from_bigquery(
        self, 
        symbol: str, 
        start: datetime, 
        end: datetime
    ) -> List[float]:
        """Query BigQuery (Cold Storage)"""
        client = self._get_bq_client()
        if not client:
            return []
            
        try:
            query = f"""
                SELECT price FROM `{BIGQUERY_TABLE}`
                WHERE symbol = @symbol
                AND timestamp BETWEEN @start AND @end
                ORDER BY timestamp ASC
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("symbol", "STRING", symbol),
                    bigquery.ScalarQueryParameter("start", "TIMESTAMP", start),
                    bigquery.ScalarQueryParameter("end", "TIMESTAMP", end),
                ]
            )
            
            job = client.query(query, job_config=job_config)
            rows = job.result()
            
            return [float(row.price) for row in rows]
            
        except Exception as e:
            logger.error(f"BigQuery query failed: {e}")
            return []
    
    def calculate_variance(self, data: List[float]) -> float:
        """
        Calculate variance using the mathematical formula:
        
        σ² = (1/n) Σᵢ₌₁ⁿ (xᵢ - μ)²
        
        Where:
        - n = number of data points
        - μ = mean of the data
        - xᵢ = each data point
        """
        if not data or len(data) == 0:
            return 0.0
            
        n = len(data)
        
        # 1. Calculate mean (μ)
        mu = sum(data) / n
        
        # 2. Calculate sum of squared differences: Σ(xᵢ - μ)²
        sum_sq_diff = sum((x - mu) ** 2 for x in data)
        
        # 3. Calculate variance: σ² = (1/n) × Σ(xᵢ - μ)²
        variance = sum_sq_diff / n
        
        return variance
    
    def calculate_std_deviation(self, data: List[float]) -> float:
        """Calculate standard deviation: σ = √(σ²)"""
        variance = self.calculate_variance(data)
        return np.sqrt(variance) if variance > 0 else 0.0
    
    async def get_market_analysis(
        self, 
        symbol: str, 
        lookback_days: int = 7
    ) -> Dict:
        """
        Full market analysis using smart Hot/Cold routing.
        
        Returns statistics including variance calculation.
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(days=lookback_days)
        
        # Fetch data with smart routing
        prices = await self.get_price_data(symbol, start_time, end_time)
        
        # Calculate statistics
        variance = self.calculate_variance(prices)
        std_dev = self.calculate_std_deviation(prices)
        mean_price = np.mean(prices) if prices else 0
        
        # Determine data source
        hot_threshold = datetime.now() - timedelta(hours=HOT_STORAGE_HOURS)
        if start_time >= hot_threshold:
            source = "HOT (Cloud SQL)"
        elif end_time < hot_threshold:
            source = "COLD (BigQuery)"
        else:
            source = "HYBRID (Cloud SQL + BigQuery)"
        
        return {
            "symbol": symbol,
            "data_points": len(prices),
            "mean_price": float(mean_price),
            "variance": float(variance),
            "std_deviation": float(std_dev),
            "analysis_period": f"{lookback_days} days",
            "storage_source": source,
            "formula": "σ² = (1/n) Σ(xᵢ - μ)²"
        }


# Singleton instance
stats_module = StatisticsModule()
