"""
Alert System for Market Predictor ML

Provides price alerts, volatility alerts, and portfolio notifications.
"""

import sqlite3
import time
from typing import Any, Dict, List, Optional

from .logging_config import setup_logging

logger = setup_logging()


class AlertDB:
    """Database manager for alerts."""

    def __init__(self, db_path: str = "data/market_predictor.db"):
        """Initialize AlertDB with database path."""
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize alerts table."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                asset_type TEXT NOT NULL,
                ticker TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                priority TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                threshold_value REAL,
                current_value REAL,
                is_read INTEGER DEFAULT 0,
                created_at REAL NOT NULL,
                read_at REAL,
                metadata TEXT
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alerts_user_read
            ON alerts(user_id, is_read, created_at DESC)
        """)

        conn.commit()
        conn.close()
        logger.info("Alert database initialized")

    def create_alert(
        self,
        user_id: str,
        asset_type: str,
        ticker: str,
        alert_type: str,
        priority: str,
        title: str,
        message: str,
        threshold_value: Optional[float] = None,
        current_value: Optional[float] = None,
        metadata: Optional[str] = None,
    ) -> int:
        """Create a new alert."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO alerts (
                user_id, asset_type, ticker, alert_type, priority,
                title, message, threshold_value, current_value,
                created_at, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                user_id,
                asset_type,
                ticker,
                alert_type,
                priority,
                title,
                message,
                threshold_value,
                current_value,
                time.time(),
                metadata,
            ),
        )

        alert_id = cursor.lastrowid
        conn.commit()
        conn.close()

        logger.info(f"Alert created: {alert_id} - {title}")
        return alert_id

    def get_alerts(
        self,
        user_id: str,
        unread_only: bool = False,
        priority: Optional[str] = None,
        asset_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get alerts for a user with optional filters."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM alerts WHERE user_id = ?"
        params = [user_id]

        if unread_only:
            query += " AND is_read = 0"

        if priority:
            query += " AND priority = ?"
            params.append(priority)

        if asset_type:
            query += " AND asset_type = ?"
            params.append(asset_type)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        alerts = [dict(row) for row in rows]
        return alerts

    def mark_read(self, alert_ids: List[int]) -> int:
        """Mark alerts as read."""
        if not alert_ids:
            return 0

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        placeholders = ",".join("?" * len(alert_ids))
        cursor.execute(
            f"""-- nosec B608 - Safe: placeholders are ? and values are parameterized
            UPDATE alerts
            SET is_read = 1, read_at = ?
            WHERE alert_id IN ({placeholders})
        """,
            [time.time()] + alert_ids,
        )

        updated = cursor.rowcount
        conn.commit()
        conn.close()

        logger.info(f"Marked {updated} alerts as read")
        return updated

    def delete_old_alerts(self, user_id: str, older_than_days: int = 30) -> int:
        """Delete old read alerts."""
        cutoff_time = time.time() - (older_than_days * 24 * 60 * 60)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM alerts
            WHERE user_id = ? AND is_read = 1 AND created_at < ?
        """,
            (user_id, cutoff_time),
        )

        deleted = cursor.rowcount
        conn.commit()
        conn.close()

        logger.info(f"Deleted {deleted} old alerts for user {user_id}")
        return deleted

    def get_unread_count(self, user_id: str) -> int:
        """Get count of unread alerts."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM alerts WHERE user_id = ? AND is_read = 0", (user_id,))

        count = cursor.fetchone()[0]
        conn.close()

        return count


class AlertGenerator:
    """Generate alerts based on market conditions."""

    def __init__(self, alert_db: AlertDB):
        """Initialize with AlertDB instance."""
        self.db = alert_db

    def check_price_alert(
        self,
        user_id: str,
        ticker: str,
        current_price: float,
        target_price: float,
        alert_type: str = "above",
    ):
        """Check if price has crossed threshold and create alert."""
        if alert_type == "above" and current_price >= target_price:
            self.db.create_alert(
                user_id=user_id,
                asset_type="stock",
                ticker=ticker,
                alert_type="price_alert",
                priority="high",
                title=f"{ticker} Price Alert",
                message=f"{ticker} has reached ${current_price:.2f} (target: ${target_price:.2f})",
                threshold_value=target_price,
                current_value=current_price,
            )
        elif alert_type == "below" and current_price <= target_price:
            self.db.create_alert(
                user_id=user_id,
                asset_type="stock",
                ticker=ticker,
                alert_type="price_alert",
                priority="high",
                title=f"{ticker} Price Alert",
                message=(
                    f"{ticker} has dropped to ${current_price:.2f} "
                    f"(target: ${target_price:.2f})"
                ),
                threshold_value=target_price,
                current_value=current_price,
            )

    def create_volatility_alert(
        self, user_id: str, ticker: str, volatility: float, threshold: float = 0.05
    ):
        """Create alert for high volatility."""
        if volatility > threshold:
            self.db.create_alert(
                user_id=user_id,
                asset_type="stock",
                ticker=ticker,
                alert_type="volatility",
                priority="medium",
                title=f"{ticker} High Volatility",
                message=(
                    f"{ticker} volatility is {volatility*100:.1f}% "
                    f"(threshold: {threshold*100:.1f}%)"
                ),
                threshold_value=threshold,
                current_value=volatility,
            )

    def create_recommendation_alert(
        self,
        user_id: str,
        ticker: str,
        action: str,
        confidence: float,
        reason: str,
        asset_type: str = "stock",
    ):
        """Create alert for ML recommendation."""
        self.db.create_alert(
            user_id=user_id,
            asset_type=asset_type,
            ticker=ticker,
            alert_type="recommendation",
            priority="high" if confidence > 0.8 else "medium",
            title=f"{action} {ticker}",
            message=(
                f"AI recommends {action} {ticker}: {reason} " f"(confidence: {confidence*100:.0f}%)"
            ),
            threshold_value=0.7,
            current_value=confidence,
        )


# Legacy compatibility
class AlertManager:
    """Legacy alert manager for backwards compatibility"""

    def send_alert(self, message: str, severity: str = "info"):
        """Placeholder for sending alerts"""
        pass


# Global instances
alert_db = AlertDB()
alert_generator = AlertGenerator(alert_db)
alert_manager = AlertManager()  # For backwards compatibility
