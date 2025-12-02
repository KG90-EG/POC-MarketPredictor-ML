"""
Database models and utilities for Trading Fun API.

This module provides SQLite database setup for user features:
- Watchlists/Portfolios
- Price Alerts
- Notifications
"""

import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Database file location
DB_PATH = Path(__file__).parent.parent / "data" / "market_predictor.db"
DB_PATH.parent.mkdir(exist_ok=True)


@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # Enable column access by name
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        conn.close()


def init_database():
    """Initialize database with required tables."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Watchlists table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS watchlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Watchlist items table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS watchlist_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                watchlist_id INTEGER NOT NULL,
                ticker TEXT NOT NULL,
                asset_type TEXT DEFAULT 'stock',
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (watchlist_id) REFERENCES watchlists(id) ON DELETE CASCADE,
                UNIQUE(watchlist_id, ticker)
            )
        """
        )

        # Create index for faster queries
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_watchlist_user
            ON watchlists(user_id)
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_watchlist_items_watchlist
            ON watchlist_items(watchlist_id)
        """
        )

        # Migration: Add asset_type column to existing tables if not exists
        try:
            cursor.execute("SELECT asset_type FROM watchlist_items LIMIT 1")
        except sqlite3.OperationalError:
            logger.info("Adding asset_type column to watchlist_items table")
            cursor.execute(
                """
                ALTER TABLE watchlist_items
                ADD COLUMN asset_type TEXT DEFAULT 'stock'
            """
            )

        logger.info("Database initialized successfully")


class WatchlistDB:
    """Database operations for watchlists."""

    @staticmethod
    def create_watchlist(user_id: str, name: str, description: Optional[str] = None) -> int:
        """Create a new watchlist."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO watchlists (user_id, name, description) VALUES (?, ?, ?)", (user_id, name, description)
            )
            return cursor.lastrowid

    @staticmethod
    def get_user_watchlists(user_id: str) -> List[Dict[str, Any]]:
        """Get all watchlists for a user."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT w.*, COUNT(wi.id) as item_count
                FROM watchlists w
                LEFT JOIN watchlist_items wi ON w.id = wi.watchlist_id
                WHERE w.user_id = ?
                GROUP BY w.id
                ORDER BY w.updated_at DESC
                """,
                (user_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_watchlist(watchlist_id: int, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific watchlist with its items."""
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Get watchlist info
            cursor.execute("SELECT * FROM watchlists WHERE id = ? AND user_id = ?", (watchlist_id, user_id))
            watchlist = cursor.fetchone()

            if not watchlist:
                return None

            # Get watchlist items
            cursor.execute(
                """
                SELECT * FROM watchlist_items
                WHERE watchlist_id = ?
                ORDER BY added_at DESC
                """,
                (watchlist_id,),
            )
            items = [dict(row) for row in cursor.fetchall()]

            result = dict(watchlist)
            result["items"] = items
            return result

    @staticmethod
    def update_watchlist(
        watchlist_id: int, user_id: str, name: Optional[str] = None, description: Optional[str] = None
    ) -> bool:
        """Update watchlist details."""
        with get_db_connection() as conn:
            cursor = conn.cursor()

            updates = []
            params = []

            if name is not None:
                updates.append("name = ?")
                params.append(name)

            if description is not None:
                updates.append("description = ?")
                params.append(description)

            if not updates:
                return False

            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.extend([watchlist_id, user_id])

            query = f"UPDATE watchlists SET {', '.join(updates)} WHERE id = ? AND user_id = ?"
            cursor.execute(query, params)

            return cursor.rowcount > 0

    @staticmethod
    def delete_watchlist(watchlist_id: int, user_id: str) -> bool:
        """Delete a watchlist and all its items."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM watchlists WHERE id = ? AND user_id = ?", (watchlist_id, user_id))
            return cursor.rowcount > 0

    @staticmethod
    def add_stock_to_watchlist(
        watchlist_id: int, user_id: str, ticker: str, notes: Optional[str] = None, asset_type: str = "stock"
    ) -> bool:
        """Add a stock or crypto to a watchlist."""
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Verify watchlist ownership
            cursor.execute("SELECT id FROM watchlists WHERE id = ? AND user_id = ?", (watchlist_id, user_id))
            if not cursor.fetchone():
                return False

            try:
                cursor.execute(
                    "INSERT INTO watchlist_items (watchlist_id, ticker, asset_type, notes) VALUES (?, ?, ?, ?)",
                    (watchlist_id, ticker.upper(), asset_type, notes),
                )

                # Update watchlist timestamp
                cursor.execute("UPDATE watchlists SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (watchlist_id,))

                return True
            except sqlite3.IntegrityError:
                # Stock already in watchlist
                return False

    @staticmethod
    def remove_stock_from_watchlist(watchlist_id: int, user_id: str, ticker: str) -> bool:
        """Remove a stock from a watchlist."""
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Verify watchlist ownership
            cursor.execute("SELECT id FROM watchlists WHERE id = ? AND user_id = ?", (watchlist_id, user_id))
            if not cursor.fetchone():
                return False

            cursor.execute("DELETE FROM watchlist_items WHERE watchlist_id = ? AND ticker = ?", (watchlist_id, ticker.upper()))

            if cursor.rowcount > 0:
                # Update watchlist timestamp
                cursor.execute("UPDATE watchlists SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (watchlist_id,))
                return True

            return False

    @staticmethod
    def get_watchlist_tickers(watchlist_id: int, user_id: str) -> List[str]:
        """Get all ticker symbols in a watchlist."""
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Verify watchlist ownership
            cursor.execute("SELECT id FROM watchlists WHERE id = ? AND user_id = ?", (watchlist_id, user_id))
            if not cursor.fetchone():
                return []

            cursor.execute("SELECT ticker FROM watchlist_items WHERE watchlist_id = ?", (watchlist_id,))
            return [row[0] for row in cursor.fetchall()]


# Initialize database on module import
try:
    init_database()
    logger.info(f"Database ready at: {DB_PATH}")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")
