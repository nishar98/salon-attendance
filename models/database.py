"""Database connection pool management."""

import os
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Connection pool (min 1, max 5 connections — plenty for 6 users)
_connection_pool = None


def get_pool():
    """Get or create the database connection pool."""
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = pool.SimpleConnectionPool(
            minconn=1,
            maxconn=5,
            dsn=DATABASE_URL,
        )
    return _connection_pool


def get_db():
    """Get a database connection from the pool. Use as a context manager."""
    db_pool = get_pool()
    conn = db_pool.getconn()
    try:
        yield conn
    finally:
        db_pool.putconn(conn)


def close_pool():
    """Close all connections in the pool. Call on app shutdown."""
    global _connection_pool
    if _connection_pool is not None:
        _connection_pool.closeall()
        _connection_pool = None
