from BinomoAPI.config.conf import Config
from BinomoAPI.wss.client import WebSocketClient
import requests
import asyncio

class BinomoAPI:
    def __init__(self, AuthToken: str, device_id: str, demo: bool = False):
        self.walletType = None
        if demo:
            self.walletType = "demo"
        else:
            self.walletType = "real"
        self.AuthToken = AuthToken
        self.device_id = device_id
        self.walletType
        self.config = Config()

        self.api_host = f"{self.config.API_HOST}?authtoken={self.AuthToken}&device=web&device_id={self.device_id}&?v=2&vsn=2.0.0"

        # connect
        self._connect()
    async def _connect(self):
        self.ws = WebSocketClient(self.api_host)
        self.ws.run()
    async def Getbalance(self):
        headers = {'device-id': self.device_id, 'device-type': 'web','authorization-token': self.AuthToken, 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'}
        res = requests.get("https://api.binomo.com/bank/v1/read?locale=en",headers=headers).json()
        for i in res["data"]:
            if i["account_type"] == self.walletType:
                return i["amount"]/100
