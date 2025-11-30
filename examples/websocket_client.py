"""
Example WebSocket client for testing real-time price updates.

Usage:
    python examples/websocket_client.py
"""
import asyncio
import websockets
import json
import sys


async def test_websocket():
    """Connect to WebSocket and subscribe to stock updates."""
    uri = "ws://localhost:8000/ws/example_client"
    
    print(f"Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✓ Connected!")
            
            # Subscribe to AAPL
            print("\nSubscribing to AAPL...")
            await websocket.send(json.dumps({
                "action": "subscribe",
                "ticker": "AAPL"
            }))
            
            # Subscribe to MSFT
            print("Subscribing to MSFT...")
            await websocket.send(json.dumps({
                "action": "subscribe",
                "ticker": "MSFT"
            }))
            
            # Subscribe to NVDA
            print("Subscribing to NVDA...")
            await websocket.send(json.dumps({
                "action": "subscribe",
                "ticker": "NVDA"
            }))
            
            print("\n✓ Subscribed to 3 tickers. Waiting for updates...")
            print("(Updates arrive every 30 seconds)")
            print("Press Ctrl+C to exit\n")
            
            # Listen for updates
            message_count = 0
            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=60)
                    data = json.loads(message)
                    
                    message_count += 1
                    
                    if data['type'] == 'subscribed':
                        print(f"[{message_count}] ✓ Subscribed to {data['ticker']}")
                    
                    elif data['type'] == 'price_update':
                        ticker = data['ticker']
                        price = data['price']
                        change = data['change']
                        change_pct = data['change_percent']
                        timestamp = data['timestamp']
                        
                        # Color-coded output
                        color = '\033[92m' if change >= 0 else '\033[91m'  # Green or Red
                        reset = '\033[0m'
                        
                        print(f"[{message_count}] {ticker:5} ${price:8.2f} "
                              f"{color}{change:+7.2f} ({change_pct:+6.2f}%){reset} "
                              f"@ {timestamp[11:19]}")
                    
                    else:
                        print(f"[{message_count}] Received: {data}")
                
                except asyncio.TimeoutError:
                    print("\n⏱ No updates for 60 seconds. Sending ping...")
                    await websocket.send(json.dumps({"action": "ping"}))
    
    except websockets.exceptions.ConnectionClosed:
        print("\n✗ Connection closed")
    except KeyboardInterrupt:
        print("\n\n✓ Disconnected by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("WebSocket Real-Time Price Updates - Example Client")
    print("=" * 60)
    
    try:
        asyncio.run(test_websocket())
    except KeyboardInterrupt:
        print("\nExiting...")
