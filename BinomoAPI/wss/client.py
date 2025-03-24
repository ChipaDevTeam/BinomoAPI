import asyncio
import websockets

class WebSocketClient:
    def __init__(self, uri, headers=None):
        self.uri = uri

    async def connect(self):
        async with websockets.connect(self.uri) as websocket:
            self.websocket = websocket
            await self.listen()

    async def send(self, message):
        if self.websocket:
            await self.websocket.send(message)

    async def listen(self):
        try:
            async for message in self.websocket:
                print(f"Received: {message}")
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed")

    def run(self):
        asyncio.run(self.connect())