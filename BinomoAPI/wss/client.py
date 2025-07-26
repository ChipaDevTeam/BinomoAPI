import asyncio
import websockets
import logging
import json
from typing import Optional

class WebSocketClient:
    def __init__(self, uri: str = None, headers: Optional[dict] = None, auth_token: str = None, device_id: str = None, session=None):
        # Initialize logger first
        self.logger = logging.getLogger(__name__)
        
        # Build the correct Binomo WebSocket URL
        if uri is None:
            self.uri = "wss://ws.binomo.com/?v=2&vsn=2.0.0"
        else:
            self.uri = uri
            
        # Build headers with session cookies (THIS IS THE KEY!)
        if headers is None:
            self.headers = {
                "Origin": "https://binomo.com",
                "Cache-Control": "no-cache", 
                "Accept-Language": "en-US,en;q=0.9,es;q=0.8,fr;q=0.7",
                "Pragma": "no-cache",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 OPR/120.0.0.0",
                "Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits"
            }
            
            # Add session cookies if available (THIS FIXES THE CONNECTION!)
            if session and hasattr(session, 'cookies'):
                cookie_header = "; ".join([f"{cookie.name}={cookie.value}" for cookie in session.cookies])
                self.headers["Cookie"] = cookie_header
                self.logger.info(f"🍪 Using session cookies for WebSocket authentication")
            
            # Add authentication headers if available
            if auth_token:
                self.headers.update({
                    "authorization-token": auth_token
                })
            
            if device_id:
                self.headers.update({
                    "device-id": str(device_id),
                    "device-type": "web"
                })
        else:
            self.headers = headers
            
        self.auth_token = auth_token
        self.device_id = device_id
        self.session = session
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self._connected = False
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.info(f"WebSocketClient initialized with FIXED session-based authentication")
        self.logger.info(f"URI: {self.uri}")

    async def connect(self):
        """Establish WebSocket connection using session-based authentication (FIXED!)."""
        try:
            self.logger.info("🔗 Attempting WebSocket connection with session cookies (FIXED METHOD)...")
            self.logger.info(f"🌐 URI: {self.uri}")
            self.logger.info(f"🔑 Headers: {list(self.headers.keys())}")
            
            # Connect with session cookies - THIS IS THE FIX!
            self.websocket = await websockets.connect(
                self.uri, 
                extra_headers=self.headers,
                timeout=30
            )
            self._connected = True
            self.logger.info("🎉 WebSocket connected successfully with session cookies!")
            
            # Send authentication if we have credentials
            if self.auth_token and self.device_id:
                await self._authenticate()
            
            # Start listening for messages in the background
            asyncio.create_task(self.listen())
            
            return True
            
        except websockets.exceptions.InvalidStatusCode as e:
            self._connected = False
            self.logger.error(f"❌ WebSocket connection failed with status {e.status_code}")
            raise Exception(f"WebSocket connection failed: HTTP {e.status_code}")
            
        except Exception as e:
            self._connected = False
            self.logger.error(f"❌ Connection error: {e}")
            raise

    async def _authenticate(self):
        """Send authentication message using Phoenix/Elixir WebSocket format"""
        try:
            auth_message = {
                "topic": "auth",
                "event": "phx_join", 
                "payload": {
                    "token": self.auth_token,
                    "device_id": str(self.device_id)
                },
                "ref": "1"
            }
            
            await self.send_json(auth_message)
            self.logger.info("🔐 Authentication message sent via WebSocket")
            
        except Exception as e:
            self.logger.error(f"❌ WebSocket authentication failed: {e}")

    async def send(self, message: str):
        """Send message through WebSocket."""
        if not self._connected or not self.websocket:
            await self.connect()
            
        try:
            await self.websocket.send(message)
            self.logger.debug(f"📤 Sent: {message}")
        except websockets.exceptions.ConnectionClosed:
            self._connected = False
            self.logger.warning("⚠️ WebSocket connection closed during send")
            raise
        except Exception as e:
            self.logger.error(f"❌ Send error: {e}")
            raise

    async def send_json(self, data: dict):
        """Send JSON message through WebSocket"""
        message = json.dumps(data)
        await self.send(message)

    async def listen(self):
        """Listen for incoming messages."""
        try:
            if not self.websocket:
                return
                
            async for message in self.websocket:
                self.logger.debug(f"Received: {message}")
                # You can add message handling logic here
                
        except websockets.exceptions.ConnectionClosed:
            self._connected = False
            self.logger.warning("WebSocket connection closed")
        except Exception as e:
            self._connected = False
            self.logger.error(f"Listening error: {e}")

    async def close(self):
        """Close WebSocket connection."""
        if self.websocket:
            try:
                await self.websocket.close()
                self._connected = False
                self.logger.info("WebSocket connection closed")
            except Exception as e:
                self.logger.error(f"Error closing WebSocket: {e}")

    async def run(self):
        """Establish connection (legacy method for compatibility)."""
        await self.connect()