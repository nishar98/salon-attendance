"""Database connection management."""

import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_db():
    """Get a database connection. Opens a fresh connection per request (fine for 10 users)."""
    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    try:
        yield conn
    finally:
        conn.close()


def close_pool():
    """No-op for compatibility (no pool used)."""
    pass
