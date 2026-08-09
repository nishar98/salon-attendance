"""Database connection pool management."""

import os
from dotenv import load_dotenv
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Connection pool (min 1, max 5 connections — plenty for 6 users)
_connection_pool = None


def get_pool():
    """Get or create the database connection pool."""
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = ConnectionPool(
            conninfo=DATABASE_URL,
            min_size=1,
            max_size=5,
            kwargs={"row_factory": dict_row},
        )
    return _connection_pool


def get_db():
    """Get a database connection from the pool."""
    pool = get_pool()
    with pool.connection() as conn:
        yield conn


def close_pool():
    """Close all connections in the pool. Call on app shutdown."""
    global _connection_pool
    if _connection_pool is not None:
        _connection_pool.close()
        _connection_pool = None
