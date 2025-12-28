"""
Database Configuration for PostgreSQL
Supports: Connection Pooling, Environment Variables, Transaction Management
"""

import os
from typing import Optional, List, Dict, Any
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """PostgreSQL Database Configuration"""

    def __init__(self):
        # Environment Variables (überschreiben Defaults)
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = int(os.getenv("DB_PORT", "5432"))
        self.database = os.getenv("DB_NAME", "jobmining")
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "postgres")

        # Connection Pool Settings
        self.min_connections = int(os.getenv("DB_MIN_CONN", "2"))
        self.max_connections = int(os.getenv("DB_MAX_CONN", "10"))

        # Connection Pool
        self._pool: Optional[pool.ThreadedConnectionPool] = None

    def get_connection_string(self) -> str:
        """Returns PostgreSQL connection string"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    def initialize_pool(self):
        """Initialize connection pool"""
        if self._pool is None:
            try:
                self._pool = psycopg2.pool.ThreadedConnectionPool(
                    self.min_connections,
                    self.max_connections,
                    host=self.host,
                    port=self.port,
                    database=self.database,
                    user=self.user,
                    password=self.password,
                    cursor_factory=RealDictCursor
                )
                logger.info(f"✅ DB Pool initialized: {self.host}:{self.port}/{self.database}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize DB pool: {e}")
                raise

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        if self._pool is None:
            self.initialize_pool()

        conn = self._pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Database error: {e}")
            raise
        finally:
            self._pool.putconn(conn)

    @contextmanager
    def get_cursor(self):
        """Context manager for database cursors"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
            finally:
                cursor.close()

    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute SELECT query and return results"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()

    def execute_insert(self, query: str, params: Optional[tuple] = None) -> Optional[int]:
        """Execute INSERT and return inserted ID"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            if cursor.description:  # Has RETURNING clause
                return cursor.fetchone()
            return None

    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """Execute bulk INSERT/UPDATE"""
        with self.get_cursor() as cursor:
            cursor.executemany(query, params_list)
            return cursor.rowcount

    def close_pool(self):
        """Close connection pool"""
        if self._pool:
            self._pool.closeall()
            logger.info("✅ DB Pool closed")


# Global instance
db_config = DatabaseConfig()


# Convenience functions
def get_db():
    """Get database config instance"""
    return db_config


def init_db():
    """Initialize database connection pool"""
    db_config.initialize_pool()


def close_db():
    """Close database connection pool"""
    db_config.close_pool()
