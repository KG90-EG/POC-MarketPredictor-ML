"""
Alert system for market predictions and significant changes.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class AlertType(Enum):
    """Types of alerts"""

    SIGNAL_CHANGE = "signal_change"  # BUY/SELL/HOLD signal changed
    HIGH_CONFIDENCE = "high_confidence"  # High confidence prediction
    PRICE_SPIKE = "price_spike"  # Significant price change
    MOMENTUM_SHIFT = "momentum_shift"  # Momentum score changed significantly


class AlertPriority(Enum):
    """Alert priority levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Alert data structure"""

    alert_id: str
    alert_type: AlertType
    priority: AlertPriority
    asset_type: str  # 'stock' or 'crypto'
    symbol: str
    name: str
    message: str
    timestamp: datetime
    data: Dict = field(default_factory=dict)
    read: bool = False


class AlertManager:
    """Manages alerts and notifications"""

    def __init__(self, max_alerts: int = 100):
        self.alerts: List[Alert] = []
        self.max_alerts = max_alerts
        self.last_signals: Dict[str, str] = {}  # symbol -> last signal
        self.last_prices: Dict[str, float] = {}  # symbol -> last price
        self.last_momentum: Dict[str, float] = {}  # symbol -> last momentum

    def check_and_create_alerts(
        self, symbol: str, name: str, asset_type: str, prediction: Dict, current_price: Optional[float] = None
    ) -> List[Alert]:
        """
        Check prediction data and create alerts if needed.

        Args:
            symbol: Stock ticker or crypto ID
            name: Asset name
            asset_type: 'stock' or 'crypto'
            prediction: Prediction dictionary with signal, confidence, metrics
            current_price: Current price (optional)

        Returns:
            List of newly created alerts
        """
        new_alerts = []

        # Check for signal changes
        signal = prediction.get("signal")
        last_signal = self.last_signals.get(symbol)

        if last_signal and signal != last_signal and signal in ["BUY", "SELL"]:
            priority = AlertPriority.HIGH if signal == "BUY" else AlertPriority.MEDIUM
            alert = Alert(
                alert_id=f"{symbol}_{AlertType.SIGNAL_CHANGE.value}_{datetime.now().timestamp()}",
                alert_type=AlertType.SIGNAL_CHANGE,
                priority=priority,
                asset_type=asset_type,
                symbol=symbol,
                name=name,
                message=f"Signal changed from {last_signal} to {signal}",
                timestamp=datetime.now(),
                data={
                    "old_signal": last_signal,
                    "new_signal": signal,
                    "confidence": prediction.get("confidence"),
                    "reasoning": prediction.get("reasoning"),
                },
            )
            new_alerts.append(alert)
            logger.info(f"Alert created: {symbol} signal changed {last_signal} -> {signal}")

        # Update last signal
        self.last_signals[symbol] = signal

        # Check for high confidence BUY/SELL
        confidence = prediction.get("confidence", 0)
        if signal in ["BUY", "SELL"] and confidence >= 75:
            alert = Alert(
                alert_id=f"{symbol}_{AlertType.HIGH_CONFIDENCE.value}_{datetime.now().timestamp()}",
                alert_type=AlertType.HIGH_CONFIDENCE,
                priority=AlertPriority.HIGH if signal == "BUY" else AlertPriority.MEDIUM,
                asset_type=asset_type,
                symbol=symbol,
                name=name,
                message=f"High confidence {signal} signal ({confidence:.0f}%)",
                timestamp=datetime.now(),
                data={
                    "signal": signal,
                    "confidence": confidence,
                    "reasoning": prediction.get("reasoning"),
                    "current_price": current_price,
                },
            )
            new_alerts.append(alert)
            logger.info(f"Alert created: {symbol} high confidence {signal} ({confidence:.0f}%)")

        # Check for price spikes (stocks only)
        if current_price and symbol in self.last_prices:
            last_price = self.last_prices[symbol]
            price_change_pct = ((current_price - last_price) / last_price) * 100

            if abs(price_change_pct) >= 5:  # 5% or more change
                priority = AlertPriority.HIGH if abs(price_change_pct) >= 10 else AlertPriority.MEDIUM
                direction = "up" if price_change_pct > 0 else "down"
                alert = Alert(
                    alert_id=f"{symbol}_{AlertType.PRICE_SPIKE.value}_{datetime.now().timestamp()}",
                    alert_type=AlertType.PRICE_SPIKE,
                    priority=priority,
                    asset_type=asset_type,
                    symbol=symbol,
                    name=name,
                    message=f"Price spike {direction} {abs(price_change_pct):.1f}%",
                    timestamp=datetime.now(),
                    data={"old_price": last_price, "new_price": current_price, "change_pct": price_change_pct},
                )
                new_alerts.append(alert)
                logger.info(f"Alert created: {symbol} price spike {price_change_pct:.1f}%")

        # Update last price
        if current_price:
            self.last_prices[symbol] = current_price

        # Check for momentum shifts (crypto only)
        if asset_type == "crypto" and prediction.get("metrics"):
            momentum = prediction["metrics"].get("momentum")
            if momentum is not None and symbol in self.last_momentum:
                last_mom = self.last_momentum[symbol]
                momentum_change = momentum - last_mom

                # Alert on significant momentum shift (crossing thresholds)
                if (last_mom <= 0 and momentum > 5) or (last_mom > 5 and momentum <= 0):
                    priority = AlertPriority.HIGH if momentum > 5 else AlertPriority.MEDIUM
                    alert = Alert(
                        alert_id=f"{symbol}_{AlertType.MOMENTUM_SHIFT.value}_{datetime.now().timestamp()}",
                        alert_type=AlertType.MOMENTUM_SHIFT,
                        priority=priority,
                        asset_type=asset_type,
                        symbol=symbol,
                        name=name,
                        message=f"Momentum shifted from {last_mom:.1f} to {momentum:.1f}",
                        timestamp=datetime.now(),
                        data={"old_momentum": last_mom, "new_momentum": momentum, "change": momentum_change},
                    )
                    new_alerts.append(alert)
                    logger.info(f"Alert created: {symbol} momentum shift {momentum_change:+.1f}")

            # Update last momentum
            if momentum is not None:
                self.last_momentum[symbol] = momentum

        # Add new alerts to the list
        for alert in new_alerts:
            self.alerts.insert(0, alert)  # Insert at beginning (newest first)

        # Trim alerts if exceeding max
        if len(self.alerts) > self.max_alerts:
            self.alerts = self.alerts[: self.max_alerts]

        return new_alerts

    def get_alerts(
        self,
        unread_only: bool = False,
        priority: Optional[AlertPriority] = None,
        asset_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict]:
        """
        Get alerts with optional filters.

        Args:
            unread_only: Only return unread alerts
            priority: Filter by priority level
            asset_type: Filter by asset type ('stock' or 'crypto')
            limit: Maximum number of alerts to return

        Returns:
            List of alert dictionaries
        """
        filtered = self.alerts

        if unread_only:
            filtered = [a for a in filtered if not a.read]

        if priority:
            filtered = [a for a in filtered if a.priority == priority]

        if asset_type:
            filtered = [a for a in filtered if a.asset_type == asset_type]

        # Convert to dict for JSON response
        return [
            {
                "alert_id": a.alert_id,
                "alert_type": a.alert_type.value,
                "priority": a.priority.value,
                "asset_type": a.asset_type,
                "symbol": a.symbol,
                "name": a.name,
                "message": a.message,
                "timestamp": a.timestamp.isoformat(),
                "data": a.data,
                "read": a.read,
            }
            for a in filtered[:limit]
        ]

    def mark_as_read(self, alert_ids: List[str]) -> int:
        """
        Mark alerts as read.

        Args:
            alert_ids: List of alert IDs to mark as read

        Returns:
            Number of alerts marked as read
        """
        marked = 0
        for alert in self.alerts:
            if alert.alert_id in alert_ids:
                alert.read = True
                marked += 1
        return marked

    def clear_alerts(self, older_than_days: int = 7) -> int:
        """
        Clear old alerts.

        Args:
            older_than_days: Remove alerts older than this many days

        Returns:
            Number of alerts removed
        """
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(days=older_than_days)

        before_count = len(self.alerts)
        self.alerts = [a for a in self.alerts if a.timestamp > cutoff]
        removed = before_count - len(self.alerts)

        if removed > 0:
            logger.info(f"Cleared {removed} old alerts")

        return removed

    def get_unread_count(self) -> int:
        """Get count of unread alerts"""
        return sum(1 for a in self.alerts if not a.read)


# Global alert manager instance
alert_manager = AlertManager()
