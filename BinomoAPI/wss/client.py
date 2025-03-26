import asyncio
import websockets
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class WebSocketClient:
    def __init__(self, uri, headers=None):
        self.uri = uri
        self.websocket = None
        logging.info(f"WebSocketClient initialized with URI: {uri}")

    async def connect(self):
        try:
            logging.info("Attempting to connect to WebSocket...")
            async with websockets.connect(self.uri) as websocket:
                self.websocket = websocket
                logging.info("Connected to WebSocket")
                await self.listen()
        except Exception as e:
            logging.error(f"Connection error: {e}")

    async def send(self, message):
        if self.websocket:
            try:
                await self.websocket.send(message)
                logging.info(f"Sent: {message}")
            except Exception as e:
                logging.error(f"Send error: {e}")
        else:
            logging.warning("WebSocket is not connected. Cannot send message.")

    async def listen(self):
        try:
            async for message in self.websocket:
                logging.info(f"Received: {message}")
        except websockets.exceptions.ConnectionClosed:
            logging.warning("Connection closed")
        except Exception as e:
            logging.error(f"Listening error: {e}")

    async def run(self):
        await self.connect()