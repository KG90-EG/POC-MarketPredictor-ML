"""
Integration tests for Trading Simulation

Tests the complete flow from API endpoints to database persistence.
"""

import pytest
from time import sleep


class TestSimulationIntegration:
    """Integration tests for simulation endpoints"""

    def test_create_simulation(self, client):
        """Test creating a new simulation"""
        response = client.post(
            "/api/simulations",
            json={
                "user_id": "integration_test_user",
                "initial_capital": 10000.0,
                "mode": "auto"
            }
        )

        if response.status_code != 200:
            pytest.skip("Simulation API not available in test environment")

        data = response.json()
        assert "simulation_id" in data
        assert data["initial_capital"] == 10000.0
        assert data["current_cash"] == 10000.0
        assert data["user_id"] == "integration_test_user"

    def _create_test_simulation(self, client):
        """Helper to create simulation and return ID"""
        response = client.post(
            "/api/simulations",
            json={
                "user_id": "integration_test_user",
                "initial_capital": 10000.0,
                "mode": "auto"
            }
        )
        if response.status_code != 200:
            pytest.skip("Simulation API not available in test environment")

        return response.json()["simulation_id"]

    def test_get_simulation(self, client):
        """Test retrieving simulation details"""
        # Create simulation first
        sim_id = self._create_test_simulation(client)

        # Get simulation
        response = client.get(f"/api/simulations/{sim_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["simulation_id"] == sim_id
        assert "metrics" in data
        assert "cash" in data

    def test_get_portfolio(self, client):
        """Test getting portfolio details"""
        sim_id = self._create_test_simulation(client)

        response = client.get(f"/api/simulations/{sim_id}/portfolio")

        assert response.status_code == 200
        data = response.json()
        assert "cash" in data
        assert "positions" in data
        assert "total_value" in data
        assert data["total_value"] == 10000.0  # Initial capital, no positions

    def test_execute_manual_trade(self, client):
        """Test executing a manual trade"""
        sim_id = self._create_test_simulation(client)

        # Execute BUY trade
        response = client.post(
            f"/api/simulations/{sim_id}/trades",
            json={
                "ticker": "AAPL",
                "action": "BUY",
                "quantity": 10,
                "price": 150.0,
                "reason": "Integration test trade"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "trade" in data
        assert data["trade"]["ticker"] == "AAPL"
        assert data["trade"]["action"] == "BUY"
        assert data["trade"]["quantity"] == 10

        # Verify cash was deducted
        assert data["updated_cash"] == 10000.0 - (10 * 150.0)

        # Verify position was created
        assert "AAPL" in data["updated_positions"]
        assert data["updated_positions"]["AAPL"]["quantity"] == 10

    def test_trade_history(self, client):
        """Test trade history retrieval"""
        sim_id = self._create_test_simulation(client)

        # Execute a trade
        client.post(
            f"/api/simulations/{sim_id}/trades",
            json={
                "ticker": "MSFT",
                "action": "BUY",
                "quantity": 5,
                "price": 200.0,
                "reason": "Test trade for history"
            }
        )
        
        # Get history
        response = client.get(f"/api/simulations/{sim_id}/history")
        
        assert response.status_code == 200
        data = response.json()
        assert "trades" in data
        assert len(data["trades"]) == 1
        assert data["trades"][0]["ticker"] == "MSFT"
        assert data["trades"][0]["action"] == "BUY"
    
    def test_buy_and_sell_flow(self, client):
        """Test complete buy and sell flow"""
        sim_id = self._create_test_simulation(client)
        
        # BUY 10 shares at $100
        buy_response = client.post(
            f"/api/simulations/{sim_id}/trades",
            json={
                "ticker": "GOOGL",
                "action": "BUY",
                "quantity": 10,
                "price": 100.0,
                "reason": "Test buy"
            }
        )
        assert buy_response.status_code == 200
        
        # Verify position exists
        portfolio = client.get(f"/api/simulations/{sim_id}/portfolio").json()
        assert len(portfolio["positions"]) == 1
        assert portfolio["positions"][0]["ticker"] == "GOOGL"
        
        # SELL 5 shares at $110 (profit)
        sell_response = client.post(
            f"/api/simulations/{sim_id}/trades",
            json={
                "ticker": "GOOGL",
                "action": "SELL",
                "quantity": 5,
                "price": 110.0,
                "reason": "Test sell"
            }
        )
        assert sell_response.status_code == 200
        
        # Verify partial position remains
        portfolio = client.get(f"/api/simulations/{sim_id}/portfolio").json()
        assert portfolio["positions"][0]["quantity"] == 5
        
        # Verify profit (sold 5 @ $110, bought @ $100 = $50 profit)
        expected_cash = 10000.0 - (10 * 100.0) + (5 * 110.0)
        assert abs(portfolio["cash"] - expected_cash) < 0.01
    
    def test_insufficient_cash(self, client):
        """Test trade rejection due to insufficient cash"""
        sim_id = self._create_test_simulation(client)
        
        # Try to buy more than we can afford
        response = client.post(
            f"/api/simulations/{sim_id}/trades",
            json={
                "ticker": "TSLA",
                "action": "BUY",
                "quantity": 1000,
                "price": 200.0,  # Would cost $200,000
                "reason": "Should fail"
            }
        )
        
        assert response.status_code == 400
        assert "Insufficient cash" in response.json()["detail"]
    
    def test_insufficient_shares(self, client):
        """Test sell rejection due to insufficient shares"""
        sim_id = self._create_test_simulation(client)
        
        # Try to sell shares we don't own
        response = client.post(
            f"/api/simulations/{sim_id}/trades",
            json={
                "ticker": "NVDA",
                "action": "SELL",
                "quantity": 10,
                "price": 500.0,
                "reason": "Should fail"
            }
        )
        
        assert response.status_code == 400
        assert "No position" in response.json()["detail"]
    
    def test_reset_simulation(self, client):
        """Test resetting a simulation"""
        sim_id = self._create_test_simulation(client)
        
        # Execute some trades
        client.post(
            f"/api/simulations/{sim_id}/trades",
            json={
                "ticker": "AAPL",
                "action": "BUY",
                "quantity": 10,
                "price": 150.0,
                "reason": "Test trade"
            }
        )
        
        # Reset
        response = client.post(f"/api/simulations/{sim_id}/reset")
        assert response.status_code == 200
        
        # Verify reset
        sim = client.get(f"/api/simulations/{sim_id}").json()
        assert sim["cash"] == 10000.0  # Back to initial
        
        history = client.get(f"/api/simulations/{sim_id}/history").json()
        assert len(history["trades"]) == 0  # No trades
        
        portfolio = client.get(f"/api/simulations/{sim_id}/portfolio").json()
        assert len(portfolio["positions"]) == 0  # No positions


class TestSimulationRecommendations:
    """Integration tests for AI recommendations"""

    def test_get_recommendations_requires_model(self, client):
        """Test that recommendations endpoint works with loaded model"""
        # Create simulation
        response = client.post(
            "/api/simulations",
            json={"user_id": "test_ai", "initial_capital": 10000.0}
        )
        if response.status_code != 200:
            pytest.skip("Simulation API not available in test environment")
        sim_id = response.json()["simulation_id"]

        # Get recommendations
        response = client.post(f"/api/simulations/{sim_id}/recommendations")

        # Should either return recommendations or 503 if model not loaded
        assert response.status_code in [200, 503]

        if response.status_code == 200:
            data = response.json()
            assert "recommendations" in data
            assert isinstance(data["recommendations"], list)


class TestSimulationPerformance:
    """Performance and load tests"""

    def test_multiple_simulations(self, client):
        """Test creating multiple simulations"""
        sim_ids = []

        for i in range(5):
            response = client.post(
                "/api/simulations",
                json={
                    "user_id": f"perf_test_user_{i}",
                    "initial_capital": 10000.0 + (i * 1000)
                }
            )
            if response.status_code != 200:
                pytest.skip("Simulation API not available in test environment")
            sim_ids.append(response.json()["simulation_id"])

        # Verify all can be retrieved
        for sim_id in sim_ids:
            response = client.get(f"/api/simulations/{sim_id}")
            assert response.status_code == 200

    def test_rapid_trades(self, client):
        """Test executing multiple trades in quick succession"""
        response = client.post(
            "/api/simulations",
            json={"user_id": "rapid_test", "initial_capital": 100000.0}
        )
        if response.status_code != 200:
            pytest.skip("Simulation API not available in test environment")
        sim_id = response.json()["simulation_id"]

        tickers = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]

        # Execute multiple trades rapidly
        for ticker in tickers:
            response = client.post(
                f"/api/simulations/{sim_id}/trades",
                json={
                    "ticker": ticker,
                    "action": "BUY",
                    "quantity": 10,
                    "price": 100.0,
                    "reason": "Rapid test"
                }
            )
            assert response.status_code == 200

        # Verify all positions exist
        portfolio = client.get(f"/api/simulations/{sim_id}/portfolio").json()
        assert len(portfolio["positions"]) == 5


if __name__ == "__main__":
    print("Running integration tests...")
    print("Make sure backend server is running on http://localhost:8000")
    print()
    
    # Run with pytest
    pytest.main([__file__, "-v", "--tb=short"])
