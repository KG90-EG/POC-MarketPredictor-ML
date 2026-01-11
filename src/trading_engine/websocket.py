"""
WebSocket connection manager.

This module provides WebSocket management for real-time data updates.
Clients can subscribe to price updates, signal changes, and alerts.
"""

import logging
from typing import Dict, List, Set

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Manages WebSocket connections for real-time updates.

    In production, use a proper WebSocket library like `websockets` or `socket.io`.
    This is a simplified stub for testing.
    """

    def __init__(self):
        """Initialize WebSocket manager"""
        self._connections: Dict[str, Set[str]] = {
            "prices": set(),
            "signals": set(),
            "alerts": set(),
        }
        self._total_messages = 0

    async def connect(self, client_id: str, channel: str = "prices") -> None:
        """
        Register new WebSocket connection.

        Args:
            client_id: Unique client identifier
            channel: Channel to subscribe to (prices, signals, alerts)
        """
        if channel in self._connections:
            self._connections[channel].add(client_id)
            logger.info(f"Client {client_id} connected to {channel}")
        else:
            logger.warning(f"Unknown channel: {channel}")

    async def disconnect(self, client_id: str) -> None:
        """
        Disconnect client from all channels.

        Args:
            client_id: Unique client identifier
        """
        for channel in self._connections.values():
            channel.discard(client_id)
        logger.info(f"Client {client_id} disconnected")

    async def broadcast(self, channel: str, message: dict) -> int:
        """
        Broadcast message to all clients on channel.

        Args:
            channel: Channel to broadcast on
            message: Message data to send

        Returns:
            Number of clients message was sent to
        """
        if channel not in self._connections:
            return 0

        clients = self._connections[channel]
        self._total_messages += len(clients)

        # In production, actually send the message via WebSocket
        logger.debug(f"Broadcasting to {len(clients)} clients on {channel}")

        return len(clients)

    def get_stats(self) -> Dict:
        """
        Get WebSocket manager statistics.

        Returns:
            Dict with connection stats
        """
        total_connections = sum(len(clients) for clients in self._connections.values())

        return {
            "backend": "in_memory",
            "active_connections": total_connections,
            "channels": {
                channel: len(clients) for channel, clients in self._connections.items()
            },
            "total_messages_sent": self._total_messages,
        }

    def reset(self) -> None:
        """Reset all connections and stats"""
        for channel in self._connections.values():
            channel.clear()
        self._total_messages = 0


# Global WebSocket manager instance
manager = WebSocketManager()
