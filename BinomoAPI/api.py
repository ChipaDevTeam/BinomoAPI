from BinomoAPI.config.conf import Config
from BinomoAPI.wss.client import WebSocketClient
import requests
import time
import json
import logging

class BinomoAPI:
    def __init__(self, AuthToken: str, device_id: str, demo: bool = False, AddLogging: bool = False):
        self.logger = logging.getLogger(__name__) if AddLogging else None
        if AddLogging:
            logging.basicConfig(level=logging.DEBUG)
            self.logger.setLevel(logging.DEBUG)
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(handler)
        else:
            self.logger = None

        self.ws = None
        self.walletType = "demo" if demo else "real"
        self.AuthToken = AuthToken
        self.device_id = device_id
        self.config = Config()
        self.ref = 1
        self.assetRic_default = "EURO"

        with open("BinomoAPI/assets.json", "r") as f:
            self.assetList = json.load(f)

        self.api_host = f"{self.config.API_HOST}?authtoken={self.AuthToken}&device=web&device_id={self.device_id}&?v=2&vsn=2.0.0"

        # Connect
        if self.logger:
            self.logger.info("Connecting to Binomo API")
        self.ws = WebSocketClient(self.api_host)
        self.ws.run()
        if self.logger:
            self.logger.info("Connected to Binomo API")

        self.phxJoin()
    def _GetAssetRic(self,asset):
        for i in self.assetList:
            if i["name"] == asset:
                return i["ric"]
    async def connect(self):
        self.ws = WebSocketClient(self.api_host)
        self.ws.run()
    def phxJoin(self):
        self.sendWs('{"topic":"account","event":"phx_join","payload":{},"ref":"~~","join_ref":"~~"}')
        self.sendWs('{"topic":"user","event":"phx_join","payload":{},"ref":"~~","join_ref":"~~"}')
        self.sendWs('{"topic":"base","event":"phx_join","payload":{},"ref":"~~","join_ref":"~~"}')
        self.sendWs('{"topic":"cfd_zero_spread","event":"phx_join","payload":{},"ref":"~~","join_ref":"~~"}')
        self.sendWs('{"topic":"marathon","event":"phx_join","payload":{},"ref":"~~","join_ref":"~~"}')
        self.sendWs('{"topic":"asset:'+self.assetRic_default+'","event":"phx_join","payload":{},"ref":"~~","join_ref":"~~"}')
        self.logger.info("Sent all the requests")
    async def Getbalance(self):
        headers = {'device-id': self.device_id, 'device-type': 'web','authorization-token': self.AuthToken, 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'}
        res = requests.get("https://api.binomo.com/bank/v1/read?locale=en",headers=headers).json()
        for i in res["data"]:
            if i["account_type"] == self.walletType:
                return i["amount"]/100
    def sendWs(self,data):
        self.ws.send(data.replace("~~",str(self.ref)))
        self.ref+=1;self.lastSend = time.time()
    