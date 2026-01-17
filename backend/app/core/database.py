"""
TURBO-PLAN X - Database Connection Manager for Backend
"""

import psycopg2
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Optional
import redis
from loguru import logger


class DatabaseManager:
    """Manages PostgreSQL and Redis connections for FastAPI backend"""
    
    def __init__(self, database_url: str, redis_url: str):
        self.database_url = database_url
        self.redis_url = redis_url
        self.pool: Optional[SimpleConnectionPool] = None
        self.redis_client: Optional[redis.Redis] = None
    
    def initialize(self):
        """Initialize connection pools"""
        # PostgreSQL pool
        self.pool = SimpleConnectionPool(
            minconn=2,
            maxconn=20,
            dsn=self.database_url
        )
        logger.info("PostgreSQL connection pool initialized (2-20 connections)")
        
        # Redis client
        self.redis_client = redis.from_url(
            self.redis_url,
            decode_responses=True
        )
        logger.info("Redis client initialized")
    
    @contextmanager
    def get_db_connection(self):
        """Get PostgreSQL connection from pool"""
        conn = self.pool.getconn()
        # Enforce fresh view of data
        conn.autocommit = True
        try:
            yield conn
        except Exception as e:
            logger.error(f"Database error: {e}")
            raise
        finally:
            self.pool.putconn(conn)
    
    @contextmanager
    def get_db_cursor(self, dict_cursor: bool = True):
        """Get cursor with automatic connection management"""
        with self.get_db_connection() as conn:
            cursor_factory = RealDictCursor if dict_cursor else None
            cursor = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
            finally:
                cursor.close()
    
    def close(self):
        """Close all connections"""
        if self.pool:
            self.pool.closeall()
            logger.info("Database pool closed")
        
        if self.redis_client:
            self.redis_client.close()
            logger.info("Redis client closed")


# Global database manager instance
db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """Get the global database manager instance"""
    if db_manager is None:
        raise RuntimeError("Database manager not initialized")
    return db_manager
