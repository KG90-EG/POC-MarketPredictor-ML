"""
WebSocket manager for real-time market data updates.
"""

import asyncio
import logging
from typing import Dict, Set

import yfinance as yf
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections and broadcast updates."""

    def __init__(self):
        # Store active connections: {client_id: websocket}
        self.active_connections: Dict[str, WebSocket] = {}
        # Store subscriptions: {ticker: set of client_ids}
        self.subscriptions: Dict[str, Set[str]] = {}
        self._update_task = None

    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept new WebSocket connection."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"WebSocket client connected: {client_id}")

    def disconnect(self, client_id: str):
        """Remove WebSocket connection."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]

        # Remove from all subscriptions
        for ticker_subs in self.subscriptions.values():
            ticker_subs.discard(client_id)

        logger.info(f"WebSocket client disconnected: {client_id}")

    def subscribe(self, client_id: str, ticker: str):
        """Subscribe client to ticker updates."""
        if ticker not in self.subscriptions:
            self.subscriptions[ticker] = set()
        self.subscriptions[ticker].add(client_id)
        logger.info(f"Client {client_id} subscribed to {ticker}")

    def unsubscribe(self, client_id: str, ticker: str):
        """Unsubscribe client from ticker updates."""
        if ticker in self.subscriptions:
            self.subscriptions[ticker].discard(client_id)
            if not self.subscriptions[ticker]:
                del self.subscriptions[ticker]
        logger.info(f"Client {client_id} unsubscribed from {ticker}")

    async def send_personal_message(self, message: dict, client_id: str):
        """Send message to specific client."""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)

    async def broadcast_to_ticker(self, ticker: str, message: dict):
        """Broadcast message to all clients subscribed to ticker."""
        if ticker not in self.subscriptions:
            return

        disconnected = []
        for client_id in self.subscriptions[ticker]:
            if client_id in self.active_connections:
                try:
                    await self.active_connections[client_id].send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to {client_id}: {e}")
                    disconnected.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected:
            self.disconnect(client_id)

    async def fetch_and_broadcast_updates(self):
        """Periodically fetch market data and broadcast to subscribers."""
        while True:
            try:
                # Get all subscribed tickers
                tickers = list(self.subscriptions.keys())

                if tickers:
                    logger.debug(f"Fetching updates for {len(tickers)} tickers")

                    # Fetch data for all tickers
                    for ticker in tickers:
                        try:
                            stock = yf.Ticker(ticker)
                            info = stock.info
                            hist = stock.history(period="1d", interval="1m")

                            if not hist.empty:
                                current_price = float(hist["Close"].iloc[-1])
                                prev_close = info.get("previousClose", current_price)
                                change = current_price - prev_close
                                change_percent = (
                                    (change / prev_close * 100) if prev_close else 0
                                )

                                update = {
                                    "type": "price_update",
                                    "ticker": ticker,
                                    "price": current_price,
                                    "change": change,
                                    "change_percent": change_percent,
                                    "timestamp": hist.index[-1].isoformat(),
                                }

                                await self.broadcast_to_ticker(ticker, update)

                        except Exception as e:
                            logger.error(f"Error fetching update for {ticker}: {e}")

                # Wait before next update (30 seconds)
                await asyncio.sleep(30)

            except Exception as e:
                logger.error(f"Error in update loop: {e}")
                await asyncio.sleep(30)

    def start_updates(self):
        """Start the background update task."""
        if self._update_task is None or self._update_task.done():
            self._update_task = asyncio.create_task(self.fetch_and_broadcast_updates())
            logger.info("Started WebSocket update task")

    def get_stats(self) -> dict:
        """Get WebSocket statistics."""
        return {
            "active_connections": len(self.active_connections),
            "subscribed_tickers": len(self.subscriptions),
            "total_subscriptions": sum(
                len(subs) for subs in self.subscriptions.values()
            ),
        }


# Global connection manager
manager = ConnectionManager()
