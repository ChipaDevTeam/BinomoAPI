import asyncio
import websockets
import logging
from typing import Optional

class WebSocketClient:
    def __init__(self, uri: str, headers: Optional[dict] = None):
        self.uri = uri
        self.headers = headers or {}
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self._connected = False
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.info(f"WebSocketClient initialized with URI: {uri}")

    async def connect(self):
        """Establish WebSocket connection."""
        try:
            self.logger.info("Attempting to connect to WebSocket...")
            self.websocket = await websockets.connect(self.uri, extra_headers=self.headers)
            self._connected = True
            self.logger.info("Connected to WebSocket successfully")
            
            # Start listening for messages in the background
            asyncio.create_task(self.listen())
            
        except Exception as e:
            self._connected = False
            self.logger.error(f"Connection error: {e}")
            raise

    async def send(self, message: str):
        """Send message through WebSocket."""
        if not self._connected or not self.websocket:
            await self.connect()
            
        try:
            await self.websocket.send(message)
            self.logger.debug(f"Sent: {message}")
        except websockets.exceptions.ConnectionClosed:
            self._connected = False
            self.logger.warning("WebSocket connection closed during send")
            raise
        except Exception as e:
            self.logger.error(f"Send error: {e}")
            raise

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