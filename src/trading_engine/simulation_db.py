"""
Simulation Database Layer

Handles persistence of trading simulations, trades, and positions
using SQLite database.

Tables:
- simulations: Simulation metadata (capital, cash, user)
- simulation_trades: All executed trades
- simulation_positions: Current open positions
"""

import json
import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .simulation import TradingSimulation

logger = logging.getLogger(__name__)

# Database file location
DB_PATH = Path(__file__).parent.parent / "data" / "market_predictor.db"


@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # Return rows as dicts
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_simulation_tables():
    """
    Initialize simulation database tables if they don't exist.

    Creates three tables:
    - simulations: Simulation metadata
    - simulation_trades: Trade history
    - simulation_positions: Current positions
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Simulations table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS simulations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL DEFAULT 'default_user',
                initial_capital REAL NOT NULL,
                current_cash REAL NOT NULL,
                mode TEXT NOT NULL DEFAULT 'auto',
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Trades table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS simulation_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                simulation_id INTEGER NOT NULL,
                ticker TEXT NOT NULL,
                action TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                ml_confidence REAL,
                reason TEXT,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (simulation_id) REFERENCES simulations(id) ON DELETE CASCADE
            )
        """
        )

        # Positions table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS simulation_positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                simulation_id INTEGER NOT NULL,
                ticker TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                avg_cost REAL NOT NULL,
                last_price REAL NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (simulation_id) REFERENCES simulations(id) ON DELETE CASCADE,
                UNIQUE(simulation_id, ticker)
            )
        """
        )

        # Create indexes for performance
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_sim_user
            ON simulations(user_id)
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_trades_sim
            ON simulation_trades(simulation_id)
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_positions_sim
            ON simulation_positions(simulation_id)
        """
        )

        conn.commit()
        logger.info("Simulation database tables initialized")


class SimulationDB:
    """Database operations for trading simulations."""

    @staticmethod
    def create_simulation(
        user_id: str = "default_user",
        initial_capital: float = 10000.0,
        mode: str = "auto",
    ) -> int:
        """
        Create a new trading simulation.

        Args:
            user_id: User identifier
            initial_capital: Starting capital amount
            mode: 'auto' or 'manual' trading mode

        Returns:
            Simulation ID
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO simulations (user_id, initial_capital, current_cash, mode)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, initial_capital, initial_capital, mode),
            )
            simulation_id = cursor.lastrowid
            logger.info(
                f"Created simulation {simulation_id} for user {user_id} "
                f"with ${initial_capital:.2f}"
            )
            return simulation_id

    @staticmethod
    def get_simulation(simulation_id: int) -> Optional[TradingSimulation]:
        """
        Load simulation from database.

        Args:
            simulation_id: Simulation ID

        Returns:
            TradingSimulation instance or None if not found
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Get simulation metadata
            cursor.execute("SELECT * FROM simulations WHERE id = ?", (simulation_id,))
            sim_row = cursor.fetchone()

            if not sim_row:
                return None

            # Get positions
            cursor.execute(
                """
                SELECT ticker, quantity, avg_cost, last_price
                FROM simulation_positions
                WHERE simulation_id = ?
                """,
                (simulation_id,),
            )
            positions = {
                row["ticker"]: {
                    "quantity": row["quantity"],
                    "avg_cost": row["avg_cost"],
                    "current_price": row["last_price"],
                }
                for row in cursor.fetchall()
            }

            # Get trades
            cursor.execute(
                """
                SELECT ticker, action, quantity, price, reason,
                       ml_confidence, executed_at
                FROM simulation_trades
                WHERE simulation_id = ?
                ORDER BY executed_at
                """,
                (simulation_id,),
            )
            trades = [
                {
                    "ticker": row["ticker"],
                    "action": row["action"],
                    "quantity": row["quantity"],
                    "price": row["price"],
                    "reason": row["reason"],
                    "ml_confidence": row["ml_confidence"],
                    "timestamp": datetime.fromisoformat(row["executed_at"]),
                }
                for row in cursor.fetchall()
            ]

            # Create simulation instance
            sim = TradingSimulation(
                simulation_id=sim_row["id"],
                user_id=sim_row["user_id"],
                initial_capital=sim_row["initial_capital"],
                current_cash=sim_row["current_cash"],
                positions=positions,
                trades=trades,
                created_at=datetime.fromisoformat(sim_row["created_at"]),
            )

            return sim

    @staticmethod
    def save_simulation(sim: TradingSimulation):
        """
        Save simulation state to database.

        Updates cash balance and positions in database.

        Args:
            sim: TradingSimulation instance
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Update simulation cash
            cursor.execute(
                """
                UPDATE simulations
                SET current_cash = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (sim.cash, sim.simulation_id),
            )

            # Delete old positions
            cursor.execute(
                "DELETE FROM simulation_positions WHERE simulation_id = ?",
                (sim.simulation_id,),
            )

            # Insert current positions
            for ticker, pos in sim.positions.items():
                cursor.execute(
                    """
                    INSERT INTO simulation_positions
                    (simulation_id, ticker, quantity, avg_cost, last_price)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        sim.simulation_id,
                        ticker,
                        pos["quantity"],
                        pos["avg_cost"],
                        pos["current_price"],
                    ),
                )

            conn.commit()
            logger.info(f"Saved simulation {sim.simulation_id}")

    @staticmethod
    def save_trade(simulation_id: int, trade: Dict):
        """
        Save a trade to database.

        Args:
            simulation_id: Simulation ID
            trade: Trade dict from execute_trade()
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO simulation_trades
                (simulation_id, ticker, action, quantity, price,
                 ml_confidence, reason, executed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    simulation_id,
                    trade["ticker"],
                    trade["action"],
                    trade["quantity"],
                    trade["price"],
                    trade.get("ml_confidence"),
                    trade["reason"],
                    trade["timestamp"].isoformat(),
                ),
            )
            conn.commit()

    @staticmethod
    def get_user_simulations(user_id: str) -> List[Dict]:
        """
        Get all simulations for a user.

        Args:
            user_id: User identifier

        Returns:
            List of simulation metadata dicts
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, initial_capital, current_cash, mode,
                       is_active, created_at, updated_at
                FROM simulations
                WHERE user_id = ?
                ORDER BY created_at DESC
                """,
                (user_id,),
            )

            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def delete_simulation(simulation_id: int):
        """
        Delete a simulation and all related data.

        Args:
            simulation_id: Simulation ID
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM simulations WHERE id = ?", (simulation_id,))
            conn.commit()
            logger.info(f"Deleted simulation {simulation_id}")

    @staticmethod
    def reset_simulation(simulation_id: int):
        """
        Reset simulation to initial state.

        Clears all trades and positions, resets cash to initial capital.

        Args:
            simulation_id: Simulation ID
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Get initial capital
            cursor.execute("SELECT initial_capital FROM simulations WHERE id = ?", (simulation_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Simulation {simulation_id} not found")

            initial_capital = row["initial_capital"]

            # Reset cash
            cursor.execute(
                """
                UPDATE simulations
                SET current_cash = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (initial_capital, simulation_id),
            )

            # Clear trades and positions
            cursor.execute(
                "DELETE FROM simulation_trades WHERE simulation_id = ?",
                (simulation_id,),
            )
            cursor.execute(
                "DELETE FROM simulation_positions WHERE simulation_id = ?",
                (simulation_id,),
            )

            conn.commit()
            logger.info(f"Reset simulation {simulation_id}")


# Initialize tables on module import
try:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    init_simulation_tables()
except Exception as e:
    logger.error(f"Failed to initialize simulation tables: {e}")
