"""
Fixed WebSocket Client for Binomo using exact curl parameters
This implements the correct WebSocket connection that matches the working curl command
"""

import asyncio
import websockets
import logging
import json
import base64
import os
from typing import Optional, Dict, Any
from urllib.parse import urlencode

class FixedBinomoWebSocketClient:
    """WebSocket client using exact parameters from working curl command"""
    
    def __init__(self, auth_token: str, device_id: str):
        self.auth_token = auth_token
        self.device_id = device_id
        self.websocket = None
        self._connected = False
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Use exact URL from curl command
        self.uri = "wss://ws.binomo.com/?v=2&vsn=2.0.0"
        
        # Use exact headers from curl command
        self.headers = {
            "Origin": "https://binomo.com",
            "Cache-Control": "no-cache",
            "Accept-Language": "en-US,en;q=0.9,es;q=0.8,fr;q=0.7",
            "Pragma": "no-cache",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 OPR/120.0.0.0",
            "Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits"
        }
        
        self.logger.info(f"FixedBinomoWebSocketClient initialized")
        self.logger.info(f"URI: {self.uri}")
        self.logger.info(f"Auth Token: {auth_token[:20]}...")
    
    async def connect(self):
        """Connect using exact curl parameters"""
        try:
            self.logger.info("🔗 Attempting WebSocket connection with fixed parameters...")
            self.logger.info(f"🌐 URI: {self.uri}")
            self.logger.info(f"🔑 Headers: {list(self.headers.keys())}")
            
            # Connect with exact headers from curl
            self.websocket = await websockets.connect(
                self.uri,
                extra_headers=self.headers,
                timeout=30
            )
            
            self._connected = True
            self.logger.info("✅ WebSocket connected successfully with fixed parameters!")
            
            # Start authentication sequence
            await self._authenticate()
            
            # Start listening for messages
            asyncio.create_task(self._listen())
            
            return True
            
        except websockets.exceptions.InvalidStatusCode as e:
            self.logger.error(f"❌ WebSocket connection failed with status {e.status_code}")
            self.logger.error(f"   Response headers: {e.response_headers}")
            self._connected = False
            return False
            
        except Exception as e:
            self.logger.error(f"❌ WebSocket connection error: {e}")
            self._connected = False
            return False
    
    async def _authenticate(self):
        """Send authentication message after connection"""
        try:
            # Phoenix/Elixir WebSocket authentication format
            auth_message = {
                "topic": "auth",
                "event": "phx_join",
                "payload": {
                    "token": self.auth_token,
                    "device_id": self.device_id
                },
                "ref": "1"
            }
            
            await self.send_message(auth_message)
            self.logger.info("🔐 Authentication message sent")
            
        except Exception as e:
            self.logger.error(f"❌ Authentication failed: {e}")
    
    async def send_message(self, message: Dict[str, Any]):
        """Send JSON message through WebSocket"""
        if not self._connected or not self.websocket:
            raise Exception("WebSocket not connected")
        
        try:
            json_message = json.dumps(message)
            await self.websocket.send(json_message)
            self.logger.debug(f"📤 Sent: {json_message}")
            
        except Exception as e:
            self.logger.error(f"❌ Send error: {e}")
            raise
    
    async def _listen(self):
        """Listen for incoming messages"""
        try:
            while self._connected and self.websocket:
                message = await self.websocket.recv()
                await self._handle_message(message)
                
        except websockets.exceptions.ConnectionClosed:
            self.logger.warning("⚠️ WebSocket connection closed")
            self._connected = False
            
        except Exception as e:
            self.logger.error(f"❌ Listen error: {e}")
            self._connected = False
    
    async def _handle_message(self, message: str):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            self.logger.info(f"📥 Received: {data}")
            
            # Handle different message types
            if data.get("event") == "phx_reply":
                if data.get("payload", {}).get("status") == "ok":
                    self.logger.info("✅ Authentication successful!")
                else:
                    self.logger.error(f"❌ Authentication failed: {data}")
            
        except Exception as e:
            self.logger.error(f"❌ Message handling error: {e}")
    
    async def place_trade(self, asset: str, direction: str, amount: float, duration: int):
        """Place a trade through WebSocket"""
        if not self._connected:
            raise Exception("WebSocket not connected")
        
        try:
            trade_message = {
                "topic": "trading",
                "event": "place_trade",
                "payload": {
                    "asset": asset,
                    "direction": direction,  # "call" or "put"
                    "amount": amount,
                    "duration": duration
                },
                "ref": str(int(asyncio.get_event_loop().time()))
            }
            
            await self.send_message(trade_message)
            self.logger.info(f"📈 Trade placed: {direction.upper()} {asset} ${amount} for {duration}s")
            
            return trade_message
            
        except Exception as e:
            self.logger.error(f"❌ Trade placement failed: {e}")
            raise
    
    def is_connected(self):
        """Check if WebSocket is connected"""
        return self._connected and self.websocket and not self.websocket.closed
    
    async def close(self):
        """Close WebSocket connection"""
        if self.websocket:
            await self.websocket.close()
            self._connected = False
            self.logger.info("🔌 WebSocket connection closed")


# Test the fixed WebSocket client
async def test_fixed_websocket():
    """Test the fixed WebSocket client with real Binomo parameters"""
    
    print("🧪 Testing Fixed WebSocket Client")
    print("=" * 50)
    
    # You need to provide real auth token and device ID from a successful login
    # This is just for testing the connection format
    
    test_auth_token = "test-token-replace-with-real"
    test_device_id = "test-device-replace-with-real"
    
    client = FixedBinomoWebSocketClient(test_auth_token, test_device_id)
    
    try:
        print("🔗 Attempting connection with fixed parameters...")
        connected = await client.connect()
        
        if connected:
            print("✅ Connection successful!")
            
            # Wait a bit for authentication
            await asyncio.sleep(2)
            
            # Test trade placement (if authenticated)
            if client.is_connected():
                print("📈 Testing trade placement...")
                # await client.place_trade("EUR/USD", "call", 1.0, 60)
                
        else:
            print("❌ Connection failed")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        
    finally:
        await client.close()


if __name__ == "__main__":
    # Enable debug logging
    logging.basicConfig(level=logging.INFO)
    
    print("🔧 Fixed WebSocket Client for Binomo")
    print("Uses exact parameters from working curl command")
    print()
    print("To test with real credentials:")
    print("1. Get auth_token and device_id from successful login")
    print("2. Replace test values in test_fixed_websocket()")
    print("3. Run this script")
    print()
    
    # Uncomment to test (after providing real credentials):
    # asyncio.run(test_fixed_websocket())
