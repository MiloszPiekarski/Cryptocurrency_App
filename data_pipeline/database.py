"""
TURBO-PLAN X - Database Connection Manager
Handles connection to TimescaleDB and Redis
"""

import os
import psycopg2
from psycopg2.extras import execute_batch
from psycopg2.pool import SimpleConnectionPool
import redis
from contextlib import contextmanager
from typing import Optional
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    """
    Professional database connection manager with connection pooling
    """
    
    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 5432)),
            'database': os.getenv('POSTGRES_DB', 'turboplanx'),
            'user': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD', 'turboplanx_secure_password')
        }
        
        # Connection pool (min 1, max 20 connections)
        self.pool: Optional[SimpleConnectionPool] = None
        
        # Redis connection
        self.redis_client = redis.from_url(
            os.getenv('REDIS_URL', 'redis://localhost:6379'),
            decode_responses=True
        )
        
        logger.info("Database Manager initialized")
    
    def initialize_pool(self):
        """Initialize connection pool"""
        if self.pool is None:
            self.pool = SimpleConnectionPool(
                minconn=1,
                maxconn=20,
                **self.db_config
            )
            logger.success("Database connection pool created (1-20 connections)")
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections
        Usage:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                ...
        """
        if self.pool is None:
            self.initialize_pool()
        
        conn = self.pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            self.pool.putconn(conn)
    
    def test_connection(self) -> bool:
        """Test database and Redis connections"""
        try:
            # Test PostgreSQL
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
                logger.success(f"✓ PostgreSQL connected: {version[:50]}...")
                
                # Check TimescaleDB
                cursor.execute("SELECT extversion FROM pg_extension WHERE extname = 'timescaledb';")
                ts_version = cursor.fetchone()
                if ts_version:
                    logger.success(f"✓ TimescaleDB version: {ts_version[0]}")
                
                cursor.close()
            
            # Test Redis
            self.redis_client.ping()
            logger.success("✓ Redis connected")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Connection test failed: {e}")
            return False
    
    def close_all(self):
        """Close all connections"""
        if self.pool:
            self.pool.closeall()
            logger.info("Database connection pool closed")
        
        self.redis_client.close()
        logger.info("Redis connection closed")

# Global instance
db = DatabaseManager()

if __name__ == "__main__":
    # Test connections
    db.test_connection()
    db.close_all()
